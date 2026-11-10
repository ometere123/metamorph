# Metamorph — Consensus-Validated Metamorphic Testing

## Description

Metamorph is a reusable GenLayer Intelligent Contract for testing relational properties of another Intelligent Contract's decision function when no independently known correct answer exists for every input. A frozen suite defines a policy and transformation. Independent GenLayer leader/validator consensus evaluates whether that transformation is semantically valid; deterministic contract logic then compares the target's two strictly validated public-view outputs. EQUIVALENT, STRENGTHENED and WEAKENED relations produce PASS or FAIL only after VALID consensus. INVALID or AMBIGUOUS transformations become INCONCLUSIVE and cannot certify a target. Exact suite digests, immutable snapshots, role separation, current-version checks and a typed consumer make the result reusable for downstream authorization.

## Repository and network

- Repository: https://github.com/ometere123/metamorph
- Network: studionet
- Chain: 61999 / 0xf22f
- RPC: https://studio.genlayer.com/api
- Local CLI: genlayer 0.39.1
- GenVM: stable v0.2.12
- Linter: genvm-linter 0.11.0
- Direct Mode: genlayer-test 0.29.0

## Primary contract

- Registry: [0x5f31A604e9C3A9362A01A17c5be6b8a1440Db2dF](https://explorer-studio.genlayer.com/address/0x5f31A604e9C3A9362A01A17c5be6b8a1440Db2dF)
- Deployment: [0x28bcc805dbfd8fcb0069dbcd2729a1430248e2b4f557415b00510c68c5dfb966](https://explorer-studio.genlayer.com/tx/0x28bcc805dbfd8fcb0069dbcd2729a1430248e2b4f557415b00510c68c5dfb966)

## Consequential reference integration

The reference policy target is not third-party software. It is a compact eligibility-policy implementation with real input validation and a meaningful authorization consequence:

- Stable target: [0x6A3fb9a5aA12A90378c9a6b98bef38e121d5B45A](https://explorer-studio.genlayer.com/address/0x6A3fb9a5aA12A90378c9a6b98bef38e121d5B45A)
- Defective target: [0x3F52532f59E60fa5FD3495fEc40CbbbfbBaB3705](https://explorer-studio.genlayer.com/address/0x3F52532f59E60fa5FD3495fEc40CbbbfbBaB3705)
- Activation consumer: [0x5FBf59d09daAa5512A23431cDEEEe36e3Cd77D45](https://explorer-studio.genlayer.com/address/0x5FBf59d09daAa5512A23431cDEEEe36e3Cd77D45)

The stable candidate passed a frozen three-case suite. The defective
candidate failed a semantically valid equivalent tone case because it changed
ALLOW to DENY. A separate invalid transformation and an underspecified policy
both remained INCONCLUSIVE and uncertified. The qualified consumer obtained
is_certified_current from the real registry, changed its activated state once,
authorized one downstream ALLOW request, rejected a denied request and rejected
replay. Defective and ambiguous candidates could not activate.

## Verified results

- 39 offline tests passed.
- 20 Direct Mode tests passed.
- 59 total tests passed.
- Five contracts passed stable GenVM lint and schema extraction.
- Live RPC returned eth_chainId 0xf22f.
- Live registry readback: 2 targets, 4 suites, 10 cases, 5 runs.
- R-1 is PASS and historical/current certified.
- R-2 is FAIL and uncertified.
- R-3 is INVALID-to-INCONCLUSIVE and uncertified.
- R-4 is AMBIGUOUS-to-INCONCLUSIVE and uncertified.
- R-5 is an independent PASS recheck; R-1 remains unchanged.
- Unauthorized activation, failed activation and replay were rejected with
  unchanged state readbacks.
- Source retrieval through genlayer-js getContractCode matches the deployed
  raw hashes recorded in SOURCE_SHA256_MANIFEST.json.

The full ledger is [docs/REVIEWER_EVIDENCE.md](docs/REVIEWER_EVIDENCE.md); the
read-only verifier is run with npm run check:evidence.

## Reuse and limits

A builder registers a target adapter, freezes a policy and ordered cases,
captures target public-view outputs, obtains independent semantic consensus and
consumes exact current certification from another Intelligent Contract.
Metamorph does not prove target truth, fairness, off-chain facts or unchanged
bytecode. Target-declared versions are not cryptographic code attestation.
Distinct wallet addresses do not prove social independence. Direct Mode model
responses are controlled fixtures; live receipts do not expose private
validator reasoning.

## Scope

Frontend: NONE. Backend: NONE. Database: NONE. Docker: NONE. Application wallet
integration: NONE. No 61997, studionet-dev, studio-dev, studio-next or global
GenLayer CLI was used.

## Submission limitations

The policy target is an explicitly labelled reference integration rather than
an independently developed third-party contract. One historical add_case write
for C-5 is no longer indexed by the required RPC; the case, digest, snapshots,
run and final state are readable, and the missing hash is not replaced by an
unrelated transaction. The release commit passed [GitHub Actions run 42914210086](https://github.com/ometere123/metamorph/actions/runs/42914210086).
