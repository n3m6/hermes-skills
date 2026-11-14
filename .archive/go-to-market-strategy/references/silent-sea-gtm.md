# Silent Sea — GTM state (as of Sept 2026)

User's product: **Silent Sea**, confidential orderbook DEX on Solana. Full architectural teardown facts also in agent memory (condensed); this file carries the strategic working state.

## Product snapshot
- Sites/assets: silentsea.xyz (landing + manifesto, terminal aesthetic), X @silentsea_xyz, backend api.silentsea.xyz. Whitepaper PDF (authored by user, Nov 2025) at /silentsea-whitepaper.pdf.
- Architecture: orders AES-256-GCM encrypted client-side, RSA-2048 key-wrapped to an SGX TEE; TEE matches at price-time priority; Ed25519 attestations + Merkle commitments + chained state roots settled on a Solana program; time-locked withdrawals for non-custody. Sparse Merkle Tree (256 levels) account state inside enclave; SGX sealed checkpoints, crash recovery 10-100ms, Arweave archive tier.
- Selective disclosure (the MM answer): depth histogram with fading granularity (fine near spread, coarse >5% where stop-losses cluster), OIS (-1..+1 imbalance), OTR + cancel rate (spoofing signals), microprice. Planned: TEE-native algorithmic orders (server-side pegging).
- Stage: pre-launch waitlist. App shell in bundle wired to /market-info + ws /ws/orderbook-snapshot + /ws/rfq (RFQ = institutional/OTC wedge signal). Landing tickers are hardcoded demo data. Socials/docs/T&C links mostly '#' placeholders.
- Competitors (user's own table): Hyperliquid (dominant, transparent), Lighter, Hibachi (partial privacy), dYdX.
- Known claim drift to fix before launch: landing says 200k TPS/<300ms; whitepaper says 150k orders/s/sub-200ms.

## Agreed strategy (delivered verdict-first)
Two cold starts: liquidity + trust. Wedge = "Hyperliquid's speed with your cards hidden"; quantified villain = stop-hunting ($2-4B/yr, 15-20% victim losses); tech-native moat narrative = confidential execution as the rail where AI trading agents don't leak strategy (SDK/API distribution channel).
Trust stack: publish enclave source + reproducible build (MRENCLAVE match), independent audits (enclave + Solana program), verifier UI (paste state root → on-chain check), explicit threat-model doc ("hidden from other traders, verifiable against sequencer"), remove landing overclaims.
Channels: X core loop (founder-led build-in-public, proof-of-product, "stop-hunt watch" content franchise, Spaces with invited skeptics); short-form (TikTok education/brand only due to finance restrictions + US instability → mirror to YT Shorts/IG Reels; finance-education micro-creators); AI layer (LLM citation wins: HTML whitepaper, schema.org, GitHub, ecosystem indexes; monthly ChatGPT/Perplexity/Gemini self-test; agents as customers).
Liquidity: MMs signed BEFORE public launch, 2-4 deep markets, seeded book, maker rebates; histogram/OIS feed as the MM sales tool; RFQ block desk = relationship sales.
Sequence: (1) verifier+source+audits live + content franchise → (2) private beta w/ cohort #1 + MM commitments + live dashboard → (3) public launch 2-4 markets + incentives + referral (farmer-resistant) → (4) market expansion, proof-centric content.
KPIs: waitlist→funded conversion, live-book depth, MM count + spread vs Hyperliquid, verifier usage, agent SDK integrations, LLM share-of-voice on "confidential/private trading Solana".

## Four open questions (user hasn't answered — ask before executing a track)
1. Token planned or not? (changes incentive/points/airdrop design)
2. Primary wedge: retail perps (Hyperliquid-style) or institutional/RFQ first?
3. Founder identity public or pseudonymous? (trust-marketing posture)
4. Mainnet timeline + any MM commitments in motion?

## Offered next artifacts (any can be executed on approval)
- Content calendar + first 10 X threads/short-form clips
- AI-citation checklist for docs/site (LLM-grounding pass)
- MM outreach list with talking points
