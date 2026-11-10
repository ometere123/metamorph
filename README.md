# Metamorph

Metamorph is a reusable GenLayer Intelligent Contract for testing relational properties of another Intelligent Contract’s decision function when no independently known correct answer exists for every input. GenLayer consensus validates whether a frozen input transformation is semantically legitimate; deterministic contract logic then checks whether the target’s two observed outputs satisfy the required invariant.

It answers a narrower and more defensible question than “is this decision correct?” A policy may require that changing an irrelevant attribute preserves an outcome, that improving a qualification does not worsen it, or that removing a prerequisite is not treated as cosmetic. Metamorph records those relationships, obtains independent semantic consensus about the transformation, and deterministically computes `PASS`, `FAIL` or `INCONCLUSIVE`.

```text
FROZEN POLICY
      ↓
INPUT TRANSFORMATION
      ↓
INDEPENDENT LEADER / VALIDATOR SEMANTIC CONSENSUS
      ↓
TARGET PUBLIC-VIEW OUTPUT SNAPSHOT
      ↓
DETERMINISTIC RELATION COMPARATOR
      ↓
PASS / FAIL / INCONCLUSIVE
      ↓
EXACT CURRENT CERTIFICATION
      ↓
DOWNSTREAM POLICY ACTIVATION OR REFUSAL
```

The model never writes `PASS` or `FAIL`. `INVALID` and `AMBIGUOUS` semantic results become `INCONCLUSIVE` and cannot certify a target.

## Why it matters

Individually plausible decisions can still violate important relationships between cases. Metamorphic testing detects those regressions without requiring an oracle for every absolute answer. The target supplies actual public-view observations; Metamorph does not pretend that those observations prove real-world truth.

The production registry is [`contracts/metamorph.py`](contracts/metamorph.py). The compact policy-activation integration is [`contracts/policy_target.py`](contracts/policy_target.py) and [`contracts/policy_activation.py`](contracts/policy_activation.py). The policy target is an explicitly labelled reference integration, not third-party software.

## Protocol

The public lifecycle is:

`register_target → create_suite → add_case → freeze_suite → open_run → capture_case → evaluate_case → close_run`

The public registry interface remains:

- `register_target`, `create_suite`, `add_case`, `freeze_suite`
- `open_run`, `capture_case`, `evaluate_case`, `close_run`
- `is_certified`, `is_certified_current`
- `get_target`, `get_suite`, `get_case`, `get_run`, `get_snapshot`, `get_verdict`, `get_counts`

Four wallet roles are distinct at the protocol level: target registrant, suite curator, case author and independent tester. A recheck must use a different tester. These are separate addresses, not proof that the same real-world organization does not control them.

Supported relations:

| Relation | Semantic requirement | Deterministic output requirement |
| --- | --- | --- |
| `EQUIVALENT` | All decision-relevant facts remain materially unchanged | Same decision and score delta within the frozen tolerance |
| `STRENGTHENED` | A favorable factor improves and no adverse factor worsens | Decision rank and score do not decrease |
| `WEAKENED` | A favorable factor worsens and no beneficial factor improves | Decision rank and score do not increase |

Decision order is `DENY < REVIEW < ALLOW`; target scores are bounded integers from `0` to `10000`. Mixed, missing, contradictory or underspecified transformations must not be manufactured into `VALID`.

Suites freeze the policy, target binding, ordered cases, transformation notes and tolerances into a digest. Snapshots bind the run, case, target address, target-declared version, suite/case digests, both target outputs, tester and `TARGET_PUBLIC_VIEW` provenance. Adapter responses use strict JSON parsing, duplicate-key rejection, bounded shapes and typed decision/score validation.

## Consensus boundary

`evaluate_case` sends only the frozen policy and the two frozen inputs to `gl.nondet.exec_prompt`. Target outputs are deliberately absent from that semantic prompt. The leader returns a bounded `VALID`, `INVALID` or `AMBIGUOUS` result with a matching reason code and real scalar evidence paths. A validator independently executes and validates the same semantic task. The contract compares the substantive relation/reason signature, not raw prose or brittle exact path-list equality. Evidence paths still must be real, scalar, paired and include an observed changed scalar.

See [`docs/CONSENSUS.md`](docs/CONSENSUS.md) for the exact leader/validator boundary, the reproduced historical liveness defect and the correction. Direct Mode adversarial tests use controlled model responses; the live ledger separately identifies what was proved by StudioNet consensus.

## Consequential reference integration

`EligibilityPolicyTarget` is a small, production-minded reference policy with real inputs and state-free deterministic decisions. `ALLOW` requires a weekday, `verified=true`, `signed_receipt=true` and at least four years of experience; `tone` is declared cosmetic. The defective constructor variant intentionally makes urgent tone deny an otherwise eligible case.

`PolicyActivation` immutably binds the registry, target, suite, digest, expected run, candidate policy identity and authorized activation actor. It requires `is_certified_current(...) == true` before activation. After activation, a downstream `authorize(request_id, payload)` call obtains the candidate’s real policy view, records an `ALLOW` exactly once per request key and rejects denials or replay.

This demonstrates a reusable trust boundary, not a customer application. No tokens, custody, frontend, backend, database, Docker environment or application-wallet integration is involved.

## Stable StudioNet release

Required environment:

| Parameter | Value |
| --- | --- |
| Network | `studionet` |
| Chain ID | `61999` / `0xf22f` |
| RPC | `https://studio.genlayer.com/api` |
| CLI | repository-local `genlayer@0.39.1` |
| GenVM | stable `v0.2.12` |
| Linter | `genvm-linter==0.11.0` |
| Direct Mode | `genlayer-test==0.29.0` |

The current source-matched registry is [`0x5f31A604e9C3A9362A01A17c5be6b8a1440Db2dF`](https://explorer-studio.genlayer.com/address/0x5f31A604e9C3A9362A01A17c5be6b8a1440Db2dF), deployed in finalized transaction [`0x28bcc805dbfd8fcb0069dbcd2729a1430248e2b4f557415b00510c68c5dfb966`](https://explorer-studio.genlayer.com/tx/0x28bcc805dbfd8fcb0069dbcd2729a1430248e2b4f557415b00510c68c5dfb966).

Reference policy addresses:

- Stable candidate: [`0x6A3fb9a5aA12A90378c9a6b98bef38e121d5B45A`](https://explorer-studio.genlayer.com/address/0x6A3fb9a5aA12A90378c9a6b98bef38e121d5B45A)
- Deliberately defective candidate: [`0x3F52532f59E60fa5FD3495fEc40CbbbfbBaB3705`](https://explorer-studio.genlayer.com/address/0x3F52532f59E60fa5FD3495fEc40CbbbfbBaB3705)
- Qualified activation consumer: [`0x5FBf59d09daAa5512A23431cDEEEe36e3Cd77D45`](https://explorer-studio.genlayer.com/address/0x5FBf59d09daAa5512A23431cDEEEe36e3Cd77D45)
- Defective-candidate refusal consumer: [`0xd2974957F514AD183989D9D0e7168fF69d9c4ad9`](https://explorer-studio.genlayer.com/address/0xd2974957F514AD183989D9D0e7168fF69d9c4ad9)
- Ambiguous-candidate refusal consumer: [`0x3D1d346E55f2D44322912bc2A2A0CD9Ce38Ae849`](https://explorer-studio.genlayer.com/address/0x3D1d346E55f2D44322912bc2A2A0CD9Ce38Ae849)

The final registry readback is `targets=2, suites=4, cases=10, runs=5`:

- `R-1`: stable candidate, `PASS`, 3/3 cases, historical/current certification `true`.
- `R-2`: defective candidate, `FAIL` because the valid equivalent tone case observed `ALLOW → DENY`, certification `false`.
- `R-3`: invalid missing-receipt transformation, `INCONCLUSIVE`, certification `false`.
- `R-4`: genuinely underspecified policy, both cases `AMBIGUOUS / INSUFFICIENT_BASIS`, `INCONCLUSIVE`, certification `false`.
- `R-5`: independent recheck of `R-1`, `PASS`, parent preserved and current certification `true`.

The complete transaction and state ledger is [`docs/REVIEWER_EVIDENCE.md`](docs/REVIEWER_EVIDENCE.md). Run the read-only verifier with `npm run check:evidence`; add `--full` for complete transaction/receipt payloads. It never needs a wallet and exits nonzero for contradicted chain, state or source claims.

## Reproduce locally

```powershell
npm ci --ignore-scripts --no-audit --no-fund
python -m pip install -r requirements-dev.txt
npm exec -- genlayer network set studionet
npm run check:network
npm run check:live-network
npm exec -- genlayer --version
python -m compileall -q contracts tests
python -m pytest tests -q
$env:GENVM_VERSION = 'v0.2.12'
python -m genvm_linter.cli check contracts/metamorph.py --json
python -m genvm_linter.cli check contracts/fixture_target.py --json
python -m genvm_linter.cli check contracts/fixture_consumer.py --json
python -m genvm_linter.cli check contracts/policy_target.py --json
python -m genvm_linter.cli check contracts/policy_activation.py --json
python -m genvm_linter.cli schema contracts/metamorph.py --json
python -m genvm_linter.cli schema contracts/fixture_target.py --json
python -m genvm_linter.cli schema contracts/fixture_consumer.py --json
python -m genvm_linter.cli schema contracts/policy_target.py --json
python -m genvm_linter.cli schema contracts/policy_activation.py --json
python scripts/verify_source_hashes.py
npm run check:evidence
```

Direct Mode uses one contract class per VM and therefore stubs cross-contract views at the VM boundary. The actual multi-contract typed calls above were executed and read back on StudioNet; they are not inferred from Direct Mode.

## Security limits and non-claims

- A target can lie through its own adapter or return context-dependent public outputs. Metamorph certifies only the observed relationship.
- A target-declared version is not cryptographic bytecode identity. `getContractCode` source parity is proven only for the listed deployments; future target changes need a new registration and run.
- LLM semantic judgment can still be wrong. Independent validator recomputation, bounded schemas, evidence-path checks and fail-closed ambiguity reduce but do not eliminate that risk.
- Separate addresses do not prove social independence. All policy data, inputs, outputs and digests are public; do not submit secrets or PII.
- `FINALIZED` alone is not success. The evidence records consensus finality, execution result and canonical state readback separately.

No 61997, `studionet-dev`, `studio-dev`, `studio-next` or global CLI was used.

## Release

Release commit: [6f98cea676b94e56d130c15d01d2116156fbabe3](https://github.com/ometere123/metamorph/commit/6f98cea676b94e56d130c15d01d2116156fbabe3).
Its CI passed in [GitHub Actions run 42914210086](https://github.com/ometere123/metamorph/actions/runs/42914210086), including the read-only StudioNet evidence check.

## Documents

- [`docs/CONSENSUS.md`](docs/CONSENSUS.md) — semantic consensus and adversarial boundary.
- [`docs/THREAT_MODEL.md`](docs/THREAT_MODEL.md) — threats, mitigations, evidence and residual risk.
- [`docs/DEPLOY_AND_PROVE.md`](docs/DEPLOY_AND_PROVE.md) — deployment and lifecycle reproduction.
- [`docs/REVIEWER_EVIDENCE.md`](docs/REVIEWER_EVIDENCE.md) — concise reviewer checklist and evidence ledger.
- [`SUBMISSION.md`](SUBMISSION.md) — ready-to-paste submission copy.
- [`SOURCE_SHA256_MANIFEST.json`](SOURCE_SHA256_MANIFEST.json) — canonical and deployed raw hashes.

License: MIT.
