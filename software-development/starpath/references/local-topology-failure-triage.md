# Local topology and acceptance-run failure triage

Two symptom classes live here. **§1–§6**: a multi-service local run (the placement topology, an
interactive stack) reaches readiness and then never advances — a service's `/ready` answers 503
forever with `chain_reachable: false`, `epoch_pipeline_stage: "unavailable"`,
`last_accepted_epoch: null`, or an epoch that is captured but never accepted. **§7**: the run gets
most of the way through its cases and then fails an assertion that decides a state flip with no
retry. Start at the section that matches the symptom; each step is cheap and eliminates half the
remaining space.

## 1. Read the retained evidence, not the log window

A failed topology keeps its private tree under `<artifact-dir>/private-failure/`:
`logs/<service>.log` per process, `topology-manifest.json` (each process's state and pid), and
the secret-free `failure.json`. Treat the private tree as credentials and account state.

**The readiness body is the fact; the status code is not.** A 503 whose payload names
`pipeline_blocked_reason` tells you which dependency is missing (`chain_unavailable`,
`da_unavailable`, …) while the log says nothing at all — the tee-node's worker diagnostics are
gated behind `ENCRYPTED_DELTA_E2E_VERBOSE` even at `RUST_LOG=info`. Print the parsed body on a
failed wait.

## 2. Ask whether the chain is alive from outside the failing client

Get the port from the running process's own command line
(`tr '\0' ' ' < /proc/<pid>/cmdline | grep -oE -- '--port [0-9]+'`), then probe it
independently while the service is still complaining:

```bash
curl -sm 5 -X POST http://127.0.0.1:<port> -H 'content-type: application/json' \
  -d '{"jsonrpc":"2.0","id":1,"method":"eth_chainId","params":[]}'
```

If that answers in tens of milliseconds while a service reports the chain unreachable, the
chain is fine and the suspect is that service's own client (transport, timeout, or state check).
Sample per-process file descriptors and socket states at the same time
(`ls /proc/<pid>/fd | wc -l`, `ss -tn`) to rule out fd or connection exhaustion.

## 3. Capture the exchange on loopback

```bash
sudo tcpdump -i lo -nn -s 0 -w cap.pcap "tcp port <port>"      # then
sudo tcpdump -r cap.pcap -nn -tt -A 'tcp port <port>' > dump.txt
```

The JSON-RPC bodies are plaintext, so the dump holds both directions. Read it in this order:

1. **Was the request ever sent?** Reassemble the client payload (the body starts at `{"method"`
   or `{"jsonrpc"`; the captured ASCII is padded, so cut the object at its matching closing
   brace). A method census over the whole dump (`grep -oE '"method":"[A-Za-z_]+"'`) shows which
   step of a multi-call flow was reached: for a contract submission, missing
   `eth_sendRawTransaction` while `eth_estimateGas` repeats means the failure is **before** the
   send, not in transport.
2. **Was it answered?** For one client port, list the conversation: connect, request, then
   either a response or nothing.
3. **Who is the client?** `user-agent: foundry/1.8.1` is `cast`/`forge`; the Rust services send
   their provider's agent. Do not attribute a connection to a service by port alone.

The decisive shape: the request reaches the server, no response follows, and the client tears
the connection down **exactly N seconds later** — N is that client's configured timeout, not a
server fault. Here N was 5.001 s against a pinned
`TEE_SETTLEMENT_RPC_TIMEOUT_MILLIS=5000`.

## 4. Measure the server side by replaying the exact request

Extract the captured body and time the same call against the still-running server, on an idle
machine:

```bash
curl -sm 120 -X POST http://127.0.0.1:<port> -H 'content-type: application/json' \
  --data-binary @body.json -w 'http=%{http_code} total=%{time_total}s\n' -o out.json
```

A `200` with a large `time_total` is a **measured server-side cost**, which is the number to
compare against the client's timeout. Measured on this workstation: `eth_estimateGas` for
`submitEpoch` needs ~5.8 s of EVM execution (~19M gas) idle, so a pinned five-second client
timeout aborts every submission before it is sent and no epoch is ever accepted — a capacity
finding, not a code defect, and one that a faster host (recorded gate host: 25:56 for the whole
run) hides completely.

## 5. Attribute an unexplained process exit

When a process vanishes mid-run, get the signal and its origin rather than guessing:

```bash
/usr/bin/strace -f -tt -e trace=signal -o signals.log <command> <args>
```

- `--- SIGHUP {si_signo=SIGHUP, si_code=SI_KERNEL} ---` — the kernel hung up the controlling
  terminal: run the whole topology detached (`setsid --fork --wait … </dev/null`). Anvil
  installs a graceful handler for SIGHUP, so its exit is reported as `code=0 signal=none`, which
  looks like a clean shutdown rather than a kill.
- `si_pid`/`si_code=SI_USER` — a user process sent it; match that pid against a process-tree
  snapshot taken at the same time (`ps -eo pid,ppid,pgid,sid,tty,stat,cmd`).
- No `signal=` but a wrapper that never logs its exit line means the wrapper itself was
  signalled, so the signal went to the process group.

## 6. Raise the timeout only as far as the measurement justifies

Three timeouts are env-overridable and default to their pinned development values:
`STARPATH_SETTLEMENT_RPC_TIMEOUT_MILLIS`, `STARPATH_SETTLEMENT_RECEIPT_TIMEOUT_MILLIS`, and
`STARPATH_TOPOLOGY_TEST_TIMEOUT_MILLIS` (the spec's own test budget). With 60 s / 60 s and a
generous test budget the full 37-case topology passes here in ~6–7 min, and the tee-node's
`/ready` then reaches `chain_reachable: true` and a non-null `last_accepted_epoch`.

**Raising them changes the acceptance *environment*, so propose it, do not settle it.** Keep the
pinned defaults as the default, document which value was overridden and the measurement that
justifies it, and say so in the result record — a run with an override is not the pinned
configuration.

## 7. An assertion that decides a state flip with no retry

Symptom: a fault-matrix assertion fails at a fixed case count with a status the run says should
already have changed (`Expected: 503, Received: 200`), and re-running reproduces it at the same case.
It is neither obviously a defect nor obviously a flake, so both blind re-runs and code archaeology
waste hours. Work it in this order.

1. **Confirm what the preceding call guarantees, from the code rather than its comment.**
   `TopologyController.stop(name)` awaits the child's `close` event (SIGTERM, then a grace deadline,
   then SIGKILL, awaiting `close` again), so the process really is dead when it returns and the
   assertion is about the *other* service noticing. A silent no-op path also exists: an untracked name
   returns without doing anything.
2. **Find who owns the asserted fact and how it is cleared.** Here `authenticated_consumer_active` is
   `self.consumer.is_some()` (`services/sequencer/src/application/ordering_v2.rs`), and only two
   event-driven sites ever clear it — a failed `try_send` in `offer_next_frame`, and the per-stream
   task that ends when the client's request stream ends (`services/sequencer/src/interface/grpc.rs`).
   There is **no liveness timeout**, so the flag outlives a dead consumer until one of them fires; a
   process dying with a frame unacknowledged (`awaiting.is_some()`) suppresses the first path.
3. **Measure the window on a live stack instead of re-running the suite.** Bring up the dev stack,
   `kill -TERM` the dependent service, and poll the endpoint every 10 ms recording the first non-200.
   Do it twice — idle, and mid-frame (`close-epoch` in the background, kill ~2 s in) — because the
   idle path is the fast one. Measured on this workstation: **45 ms idle, 97 ms with a frame in
   flight**, against an assertion that allows ~0 ms.
4. **Then decide.** A 45–100 ms propagation measured against a zero-latency assertion means the case
   measures the race, not the code. Do not call it a regression unless the artifact inputs moved, and
   do not add a timeout to the service to make it pass — that is a governed behaviour change
   (`docs/specs/sequencer-stream.md`), while making the assertion wait like its neighbours is a spec
   edit the owner decides.

Report the case count, the assertion line, and the measured window; state plainly which runs were
clean (nothing else on the host, one runner) and which were not, because a contaminated run is not
evidence for either conclusion.

## 8. Close out

- Refresh the artifact stamp only when an artifact *input* moved: the stamp records `sourceInputs`
  (the eight tree/blob hashes above) and is compared against HEAD's trees, so a web-only commit no
  longer invalidates a working root. Re-run `build` when a Rust, contract, or manifest path changed.
- Keep the investigation out of the accepted evidence: captures, signal traces, replay bodies,
  and wrapper scripts are diagnostics. Record the *finding* (the measured call cost, the
  timeout that aborts, the override used) in a `docs/results/` record, and keep every
  `private-failure/` tree out of it.
