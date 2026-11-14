# Deployed stacks on the host

Inventorying and accounting for the starpath dev stacks that run on this machine (not the local
`run-development-topology.mjs` stack, which is pty-attached and torn down).

## Layout

- `/srv/starpath/<stack>/` — runtime state per stack: `api/`, `sequencer/`, `tee/`, `rpc/`,
  `readiness/`, `public/`. Root-owned, per-role dirs 0700; a plain `du` over it spams
  "Permission denied" — that is expected, not a broken stack.
- `/opt/starpath/<commit>/` — one immutable build revision per deployed commit (`bin/`, `scripts/`).
  Many revisions accumulate; only those referenced by a running unit's `ExecStart` are live.
- Unit naming `starpath-<stack>-<role>.service`; stacks are `sepolia-rN` (public alias `pitch-rN`) and
  `nitro-NN`. **`nitro21` is unhyphenated** — enumerate with the glob `starpath*`, never reconstruct
  a name.
- Roles: `api`, `sequencer`, `reference` (python), `readiness`, `tee` (`starpath-tee-node`), `archive`
  (`starpath-fixture-delta-archive`), and `*-rpc` forwarders (`operator`, `reference`, `seq`, `tee`,
  `public-read`).
- Public entry is `caddy.service` + `/etc/caddy/Caddyfile`: one site
  (`pitch-rN.<ip>.sslip.io`, `argus.clawby.net`) proxying `/api`→api port, `/rpc`→public-read port,
  `/archive`→archive port, `/ready`→readiness port, serving the static bundle from
  `<stack>/public/web`. The file says it is rendered — edit the services descriptor, not the Caddyfile.

## Inventory procedure

1. **One enumeration, written to a file.** Do NOT loop `systemctl show` per unit from
   `execute_code` — it caps at 50 tool calls per cell and a ~60-unit inventory blows it mid-run.
   Run one bash script that emits a line per unit, redirect to a TSV, then parse in Python.
2. **Do not trust `systemctl show -p A -p B --value`.** It does not return properties in the order
   requested, so positional parsing silently swaps fields. Request `systemctl show <unit>` and grep
   the keys you want: `^(Id|Description|ActiveState|SubState|MainPID|MemoryCurrent|TasksCurrent|Result|ExecMainStatus|ActiveEnterTimestamp)=`.
3. Commands: `systemctl list-units --state=running --no-legend --plain 'starpath*'` (live),
   `list-units --all` (loaded: running + failed + dead), `list-unit-files 'starpath*'` (installed,
   including disabled). Report all three counts — installed ≫ loaded ≫ running is normal.
4. **Ports**: `/proc/<pid>/fd` is not readable across uids, so a self-written socket→pid map comes back
   empty. `ss -ltnp` needs root for the same reason; `sudo -n ss -ltnp` resolves `users:(("starpath-api",pid=…))`.
   `ss -ltn` alone still gives the port list.
5. **Wiring lives in `ExecStart`**: each `*-rpc` unit passes `<upstream-file> <port> <log-file> <label>`;
   the archive unit passes `--fixture-state <bin> --listen <host:port>`. `WorkingDirectory` names the
   stack's role dir. `systemctl show -p ExecStart -p WorkingDirectory` is enough to reconstruct it.

## Accounts

One nologin account per role: `starpath-tee`, `starpath-sequencer`, `starpath-api`,
`starpath-readiness`. **There is no `starpath` user**, so `ps -u starpath` fails with "user name does
not exist" — enumerate by unit (`MainPID`) or by cmdline matching `/opt/starpath|/srv/starpath`, then
resolve the uid from `/proc/<pid>/status`.

## Memory accounting

- Report **two numbers with labels**: the sum of per-process RSS (`/proc/<pid>/status` VmRSS), and the
  sum of per-unit `MemoryCurrent` (bytes). RSS double-counts shared library pages across processes;
  `MemoryCurrent` charges shared pages once but includes page cache, so an individual unit's
  `MemoryCurrent` can sit *below* its own RSS. Never average them or present one as the other.
- `free -m` gives the denominator; state the fraction of total RAM so the number means something.
- Stopped Docker containers (`docker ps -a`) take 0 MiB — list them as disk, not memory.
- Typical shape: the python `reference` process dominates (hundreds of MiB), `sequencer` next
  (~100 MiB), forwarders and readiness ~15–30 MiB, fixture archive ~3 MiB, `starpath-api` ~6 MiB.
  Re-measure; do not quote these as constants.

## Reading state

- **`ExecMainStatus=15`** on a dead unit means SIGTERM (deliberate stop), not a crash. `Result=exit-code`
  with `1` is a real start failure.
- `Restart=on-failure` + `StartLimitBurst=5` means a unit whose dependency is down (e.g. the stack's
  anvil/RPC at `127.0.0.1:<port>`) goes `failed` and stays there; being `enabled` only makes it retry
  and fail again at next boot. A missing anvil (`pgrep anvil` empty) explains a whole stack's
  sequencers at once.
- **A stack with only `archive` and `*-rpc` units alive, every `sequencer`/`api`/`reference` dead, is a
  leftover from a superseded run — not a deployment.** Say so instead of reporting it as running.
- "Live" evidence comes from the service, not the unit state: `GET <api>/health` → 200, a POST
  `eth_chainId` to the public RPC, and recent `admitted` lines in
  `journalctl -u <stack>-sequencer`. Journal volume for the last 24 h is a cheap liveness proxy.
- **Flag a `0.0.0.0` bind.** Services are loopback-bound; one on `0.0.0.0` bypasses Caddy's headers/CSP
  and is reachable directly. Worth surfacing whenever the question is "what is exposed".
- Containers named `starpath-nitro*` in `docker ps -a` with `Exited (0)` are finished devnet runs; they
  hold no memory.

## Shutdown and decommissioning

When the demo is over the ask is "stop it". Stop, disable and delete are **three separate scopes**;
perform only the one asked for and offer the next.

1. **Fix the scope before stopping.** The `starpath*` glob misses two things that exist only for these
   stacks: `caddy.service` (its Caddyfile holds a single site that proxies the stack, so it is in scope
   for a full stop and out of scope for "stop this one stack") and the `starpath-nitro*` Docker
   containers. Read `/etc/caddy/Caddyfile` first, then `docker ps -a`.
2. **Stop the loaded set, not just the running set** — `--all` also clears units sitting in `failed`:
   `sudo systemctl stop $(systemctl list-units --all --no-legend --plain 'starpath*' | awk '{print $1}')`
   then `sudo systemctl stop caddy.service`.
3. **Disable** as its own step:
   `sudo systemctl disable $(systemctl list-unit-files --no-pager --plain 'starpath*' | awk '$2=="enabled"{print $1}') caddy.service`.
   Stopping does not disable and disabling does not stop: an enabled unit returns at boot, and the nitro
   sequencers then fail again for lack of anvil.
4. **`sudo systemctl reset-failed 'starpath*'`** clears the `failed` flag from a previous crash — it is
   why "0 running" can still report `failed=9`.
5. **Verify from outside; the stop exit code proves nothing** (rc=0 means systemd accepted the job).
   Assert all of: `ps -eo args | grep '[s]tarpath'` empty (bracket it so grep cannot match itself), 0
   running/0 active units, every unit port gone from `ss -ltn`, caddy `inactive`, and a `free -m`
   before/after delta of roughly the RSS you measured (cgroup memory is released immediately).
6. **Do not `wc -l` the enabled listing.** `systemctl list-unit-files --state=enabled` prints a header
   row and, on a clean host, a `0 unit files listed.` trailer, so `wc -l` returns 3 and reads as "3
   still enabled". Count rows with `awk '$2=="enabled"'`.
7. **Confirm the boot surface is gone:** `find /etc/systemd/system -type l \( -name 'starpath*' -o
   -name 'caddy.service' \)` must be empty — `disable` removes the `.wants` symlink, so strays mean it
   did not take.
8. **Docker and disk are the third scope.** Exited `starpath-nitro-*` containers and the untagged
   `offchainlabs/nitro-node` image hold **no memory**, only disk. Offer `docker rm`/image prune and the
   `/opt/starpath` (one build revision per commit, GBs) and `/srv/starpath` (state/logs) trees; never
   delete container data or state on a bare "stop" instruction.
9. **Revival:** `sudo systemctl enable --now 'starpath-pitch-r11-*.service' caddy` restores a public
   stack. Never revive a `nitro-*` stack without an anvil — its sequencers exit on
   `read RPC chain ID ... 127.0.0.1:<port>` and hit `StartLimitBurst`.
10. Stop and disable leave `/srv/starpath` and `/opt/starpath` fully intact: a decommissioned host still
    carries the whole state tree and every build revision on disk.

## Naming

"silentsea" is the GitHub org (`silentsea-xyz`), not a service or unit name — everything on the host is
`starpath`. Search both, expect zero `silentsea` processes, and say that explicitly instead of implying
something is missing.
