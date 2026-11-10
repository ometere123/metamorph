# Metamorph

**A reusable metamorphic-testing Intelligent Contract for GenLayer.** No frontend, backend, database, application wallet or hosted service.

Metamorph detects decision-function inconsistencies even when the correct answer to each individual input is unknown. Instead of asking an LLM whether the target gave the *right* answer, the protocol tests whether **two executions obey a relation that must hold between their answers**.

For example, if a policy says an applicant's tone is immaterial, a neutral-toned and urgent-toned version of the same facts must produce the same decision. A target that approves one and denies the other has violated an invariant even when neither answer is independently known to be correct.

## Reviewer proof in one minute

```text
frozen suite: experience and verification matter; tone is irrelevant
input A: verified=true, experience_years=4, tone=neutral
input B: verified=true, experience_years=4, tone=urgent
                   |
                   v
 independent GenLayer validators: EQUIVALENT transformation is VALID
                   |
      +------------+-------------+
      |                          |
  stable target                broken target
  ALLOW / ALLOW               ALLOW / DENY
      |                          |
 deterministic PASS          deterministic FAIL
      |                          |
  consumer unlocks           consumer refuses
```

**The LLM does not decide PASS or FAIL.** It checks whether the test *transformation* is legitimate under the frozen policy. The decision-function output comparison is deterministic. A material input change or ambiguous transformation yields `INCONCLUSIVE`, never a false claim that the target failed or passed.

## Network and version lock

| Parameter | Required value |
| --- | --- |
| Network alias | **`studionet`** |
| Chain ID | **`61999`** (`0xf22f`) |
| RPC | `https://studio.genlayer.com/api` |
| Repository-local CLI | **`genlayer@0.39.1`** (`devDependencies` + `package-lock.json`) |
| GenVM for Direct Mode | **`v0.2.12`** |
| GenVM linter | **`genvm-linter==0.11.0`** |
| GenLayer test suite | **`genlayer-test==0.29.0`** |

Use `npm ci` and `npm exec -- genlayer ...`. Neither command requires modifying the user's global GenLayer CLI. The network guard checks the pinned version **and currently selected CLI network**. `gltest.config.yaml` explicitly defaults to `studionet`.

## Architecture

```text
Target IC's deterministic public view adapter
                    |
                 register
                    v
 Metamorph registry <---- unrelated suite owner + test author
      |                              |
      |                         freeze cases
      |                              |
      +<-----------------------------+
      |
 independent tester opens run and captures both target views
      |
      v
 immutable snapshot: target address/version, inputs, outputs, digests
      |
      v
 run_nondet_unsafe: leader checks transformation; validator RE-JUDGES
      |
      v
 VALID / INVALID / AMBIGUOUS
      |
      +-- INVALID/AMBIGUOUS ---> INCONCLUSIVE test (no certification)
      |
      +-- VALID ---> deterministic comparison of decision + score
                          |
                       PASS / FAIL
                          |
             all cases resolved, close run
                          |
                PASS exact-bound certification
                          |
               independent consumer IC
                          |
           activate only if still target-current
```

### Production interface

Only [`contracts/metamorph.py`](contracts/metamorph.py) is the production primitive. Both fixtures are explicitly demonstration-only.

| Lifecycle | Writes | Views |
| --- | --- | --- |
| Target registration | `register_target` | `get_target` |
| Suite creation | `create_suite`, `add_case`, `freeze_suite` | `get_suite`, `get_case` |
| Testing | `open_run`, `capture_case`, `evaluate_case`, `close_run` | `get_run`, `get_snapshot`, `get_verdict` |
| Certification | — | `is_certified`, `is_certified_current`, `get_counts` |

Registration, authorship, ownership and test execution must come from **four distinct wallet identities**. A recheck requires a different tester. This is role separation, *not* a guarantee of real-world independence between wallet holders.

Target adapter contract (public read-only methods):

```python
get_metamorph_manifest() -> str
# {"schema":"metamorph.adapter/1","version":"stable-version"}

evaluate_metamorph(payload: str) -> str
# {"decision":"DENY|REVIEW|ALLOW","score_bps":0..10000}
```

Target decisions are ordered `DENY < REVIEW < ALLOW`. Each comparison case pins a claimed relationship:

| Relationship | Validator checks on inputs | Deterministic output invariant |
| --- | --- | --- |
| `EQUIVALENT` | Material policy facts unchanged | Decision unchanged; score change ≤ frozen tolerance |
| `STRENGTHENED` | At least one favorable fact improves, no adverse fact worsens | Decision rank and score do not decrease |
| `WEAKENED` | At least one favorable fact worsens, no beneficial fact improves | Decision rank and score do not increase |

The suite freezes a policy, named case author, exact input pairs, transformation notes, tolerance and case order into one digest. Each captured snapshot binds target address, target version, suite digest, case digest, two observed outputs, tester and provenance `TARGET_PUBLIC_VIEW`.

## Consensus and equivalence

`evaluate_case` passes frozen policy and input pairs (never the target's outputs) to a model. The leader must return one of `VALID / INVALID / AMBIGUOUS`, a matching reason code and real scalar evidence paths from both inputs. The validator independently executes the same semantic task; a proposed leader result is accepted only if it passes strict validation and agrees with the validator's independent semantic conclusion. Paths must be real, scalar, bounded and paired across original/variant inputs. The validator compares the substantive relation and reason, not a brittle exact path-list selection; independent validators may cite different valid facts. Invented or crossed paths, inconsistent reason codes, extra fields and malformed outputs are rejected. See [`docs/CONSENSUS.md`](docs/CONSENSUS.md) for the root-cause diagnosis and correction.

Only a `VALID` relation reaches deterministic target-output comparison. This avoids conflating a bad test definition with a defective target. `run_nondet_unsafe` is used instead of exact equality on raw LLM prose. Historical verdicts cannot be edited.

### Consumer binding

`is_certified(run_id, suite_id, target_id, suite_digest)` is an immutable **historical** certification. `is_certified_current(...)` additionally checks the target's **current public manifest version**, returning false on a mismatch or unavailable target. The demonstration [`MetamorphConsumer`](contracts/fixture_consumer.py) requires current certification and only activates once.

### Verified StudioNet release

The final registry is [`0x4a7F6a372d3A686302d1c4f5f162386Ab85aFA8b`](https://explorer-studio.genlayer.com/address/0x4a7F6a372d3A686302d1c4f5f162386Ab85aFA8b), deployed in finalized-successful transaction [`0x02aebfe82ccbf12c9ec2956cc1f331a1daa72afb4553731a0bf78e2342868ce8`](https://explorer-studio.genlayer.com/tx/0x02aebfe82ccbf12c9ec2956cc1f331a1daa72afb4553731a0bf78e2342868ce8). The stable fixture produced a live exact-bound PASS, the deliberately defective fixture produced a deterministic FAIL, and an invalid transformation produced INCONCLUSIVE. The typed consumer [`0x94312d8de2282485A939953E93De097FD2acf12e`](https://explorer-studio.genlayer.com/address/0x94312d8de2282485A939953E93De097FD2acf12e) activated exactly once from the current PASS and rejected an unknown run and replay. The complete transaction ledger is [`docs/REVIEWER_EVIDENCE.md`](docs/REVIEWER_EVIDENCE.md).

## Try it locally

Prerequisites: Node.js >=20, Python 3.12, npm. The exact versions are installed locally without changing global CLI:

```bash
npm ci --ignore-scripts --no-audit --no-fund
python -m pip install -r requirements-dev.txt
npm exec -- genlayer network set studionet
npm run check:network
npm run genlayer:version
python -m pytest tests/offline -q
python -m pytest tests/direct -q
python -m genvm_linter.cli check contracts/metamorph.py --json
python -m genvm_linter.cli check contracts/fixture_target.py --json
python -m genvm_linter.cli check contracts/fixture_consumer.py --json
```

Direct Mode uses the **GenVM v0.2.12** SDK. Its target-view cross-call is stubbed at the VM boundary because Direct Mode loads only one contract class per VM; the fixture target and consumer are separately deployed and executed in dedicated Direct Mode tests. This is not live IC-to-IC evidence. See [`docs/DEPLOY_AND_PROVE.md`](docs/DEPLOY_AND_PROVE.md) for the reproducible StudioNet sequence, [`docs/CONSENSUS.md`](docs/CONSENSUS.md) for the consensus boundary, and [`docs/REVIEWER_EVIDENCE.md`](docs/REVIEWER_EVIDENCE.md) for the final receipts.

## Security, limits and non-claims

- Public inputs, outputs and policy documents are visible on-chain. Do **not** place PII, secrets, private cases or API keys into test cases.
- Target outputs are only **target-reported public views**, not proof of off-chain truth. Malicious targets can lie to their own adapter. Version strings are target-declared; version equality does not prove a bytecode digest or prevent a dishonest upgrade.
- The consensus checks semantic validity of the transformation; validator model diversity and evidence quality still matter. It does **not** certify general correctness, accuracy, fairness or safety of the target.
- `EQUIVALENT` and directional monotonicity refer only to the frozen policy. Unclear or mixed transformations must remain `INCONCLUSIVE`.
- The consumer must explicitly use `is_certified_current`; a historic PASS alone is not a permanent permission or live system-health assertion.
- The target adapter's version is target-declared. A matching version is not cryptographic bytecode attestation. This release separately verified exact deployed source bytes with `genlayer-js getContractCode`; that proof is documented in the evidence ledger and does not make arbitrary future target upgrades trustworthy.
- StudioNet transaction **FINALIZED is not by itself execution success**. Verify `SUCCESS` / `FINISHED_WITH_RETURN` and read the resulting state back before reporting deployment success.
- No administration override, hidden wallet, custody, fund settlement, privileged oracle, backend or frontend is present.

## Related work and distinction

The author's broader `equivtest` registry judges individual frozen semantic requirements against target observations and includes a full frontend. **Metamorph judges relational properties of two target executions**, then uses deterministic mathematics to detect consistency failures without knowing each absolute correct answer. The design remains standalone and useful without any application UI.

License: MIT.

## Submission materials

The concise reviewer-facing description, final addresses, live proof links and explicit limitations are collected in [`SUBMISSION.md`](SUBMISSION.md). The source hashes and deployed-address bindings are in [`SOURCE_SHA256_MANIFEST.json`](SOURCE_SHA256_MANIFEST.json).
