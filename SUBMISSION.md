# Metamorph — Consensus-Validated Metamorphic Testing for Intelligent Contracts

## Description (under 1,000 characters)

Metamorph is a reusable GenLayer Intelligent Contract for testing relational properties of another Intelligent Contract's decision function when no independently known correct answer exists for every input. A frozen suite defines a policy and metamorphic transformation. GenLayer leader/validator consensus independently determines whether the transformation is semantically valid; deterministic contract logic then compares the target's two strictly validated public-view outputs. EQUIVALENT, STRENGTHENED and WEAKENED relations produce PASS or FAIL only after VALID semantic consensus. INVALID or AMBIGUOUS transformations become INCONCLUSIVE and cannot certify a target. Immutable snapshots, role separation, exact suite digests, current-version checks and a typed consumer provide reusable downstream authorization.

## Repository and deployment

- Repository: https://github.com/ometere123/metamorph
- Network: `studionet`, chain `61999` (`0xf22f`), RPC `https://studio.genlayer.com/api`
- CLI: repository-local `genlayer@0.39.1`
- Primary registry: [`0x4a7F6a372d3A686302d1c4f5f162386Ab85aFA8b`](https://explorer-studio.genlayer.com/address/0x4a7F6a372d3A686302d1c4f5f162386Ab85aFA8b)
- Registry deployment: [`0x02aebfe82ccbf12c9ec2956cc1f331a1daa72afb4553731a0bf78e2342868ce8`](https://explorer-studio.genlayer.com/tx/0x02aebfe82ccbf12c9ec2956cc1f331a1daa72afb4553731a0bf78e2342868ce8)
- Stable-PASS consumer: [`0x94312d8de2282485A939953E93De097FD2acf12e`](https://explorer-studio.genlayer.com/address/0x94312d8de2282485A939953E93De097FD2acf12e)
- Consumer deployment: [`0x293a8d51cd2e7091066afbebe939a7c7bf77419002479347080032adae1d4fa0`](https://explorer-studio.genlayer.com/tx/0x293a8d51cd2e7091066afbebe939a7c7bf77419002479347080032adae1d4fa0)

## Verified evidence

- 36 offline tests, 15 Direct Mode tests, 51 total tests passed.
- GenVM linter `0.11.0`, stable bundle `v0.2.12`, all three contracts linted and schematized.
- Live stable fixture: exact-bound `R-1` closed `PASS`; `is_certified` and `is_certified_current` both true.
- Live defective fixture: `R-2` closed `FAIL`; certification false.
- Live invalid transformation: `R-4` closed `INCONCLUSIVE` with two `INVALID / MATERIAL_DIFFERENCE` verdicts; certification false.
- Typed consumer activated once from `R-1`, rejected unknown `R-999`, rejected replay, and a correctly bound negative consumer rejected `R-2`.
- Final deployed bytes match local source exactly via `genlayer-js getContractCode`; hashes are in [`SOURCE_SHA256_MANIFEST.json`](SOURCE_SHA256_MANIFEST.json).
- Full transaction-level evidence: [`docs/REVIEWER_EVIDENCE.md`](docs/REVIEWER_EVIDENCE.md).

## Reusability and limitations

Builders register any target exposing the bounded adapter, freeze policy/cases, run an independent tester, and consume exact current certification from another Intelligent Contract. Metamorph does not certify target truth, fairness or off-chain facts. Target versions are declared by the target and are not bytecode attestation. Direct Mode semantic tests use controlled mocks; live receipts do not expose private validator reasoning. Role separation provides distinct addresses, not guaranteed real-world independence.

## Release

Final commit SHA and final GitHub Actions run are recorded after the ordinary push and CI completion. No reviewer score is claimed.
