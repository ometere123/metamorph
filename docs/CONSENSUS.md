# Metamorph consensus design

Metamorph uses GenLayer semantic consensus for one bounded question: does a frozen pair of input objects satisfy the frozen policy and claimed metamorphic relation? It does not ask a model whether a target is correct, and it never gives target outputs to the semantic classifier as justification.

## Exact execution boundary

`evaluate_case` first verifies the open run, tester, frozen suite, captured snapshot and target bindings. The snapshot is created deterministically from the registered target’s two public views before the nondeterministic block. The semantic prompt contains only:

- frozen policy;
- claimed relation;
- transformation note;
- original and variant input objects;
- snapshot digest.

All policy, notes and input objects are delimited as untrusted data. They are not instructions. The target’s observed decisions and scores are absent from the semantic prompt.

The leader executes:

```python
gl.nondet.exec_prompt(instruction, response_format="json")
```

The validator supplied to `gl.vm.run_nondet_unsafe` independently executes the same semantic task and validates its own result. It does not receive or trust the leader’s explanation, classification or evidence list.

The accepted response is exactly:

```json
{
  "relation": "VALID | INVALID | AMBIGUOUS",
  "reason_code": "RELATION_SATISFIED | MATERIAL_DIFFERENCE | INSUFFICIENT_BASIS",
  "evidence_paths": ["original.some_scalar", "variant.some_scalar"]
}
```

The contract rejects missing/extra keys, invalid enums, contradictory reason codes, malformed JSON, duplicate evidence paths, nonexistent paths, non-scalar leaves, missing original or variant evidence, unpaired suffixes and oversized lists. Paths must include at least one paired scalar that actually changed. This prevents a leader from citing only unchanged fields while discussing a different transformation.

The validator compares the substantive signature `(relation, reason_code)`. It does not require an identical path list or raw prose because independently reasoning models can select different, equally valid paired facts. Path lists remain independently bounded and validated; they are provenance, not a substitute for recomputation. Exact path-list equality was the reproduced liveness failure in the earlier implementation.

## Deterministic boundary

Only `VALID` reaches the comparator. `INVALID` and `AMBIGUOUS` always produce `INCONCLUSIVE`; they cannot manufacture a target `FAIL`, `PASS` or certification.

For a `VALID` case, deterministic code compares strict target adapter results:

- `EQUIVALENT`: same decision and absolute score delta no greater than frozen tolerance.
- `STRENGTHENED`: variant decision rank is not lower and score is not lower.
- `WEAKENED`: variant decision rank is not higher and score is not higher.

Target decisions are ordered `DENY < REVIEW < ALLOW`; scores are integers `0..10000`. The model cannot write the case outcome. Run closure uses `FAIL` precedence, then `INCONCLUSIVE`, then all-`PASS`.

## Adversarial boundaries

The Direct Mode suite uses controlled leader/validator responses to exercise substantive attacks, not only JSON shape:

- a missing signed receipt hidden behind the same received day;
- increased experience combined with a lost verification credential;
- prompt injection in frozen policy/input text;
- a malicious well-formed leader classification;
- leader/validator disagreement;
- fabricated, irrelevant, duplicate, missing and unpaired evidence paths;
- invalid enums, mismatched reason codes, extra keys and truncated results.

The target’s observed outputs are not available to the semantic classifier in these tests. The policy activation suite separately checks exact current certification, typed target identity, authorized activation, denial and single-use downstream requests.

## Observed diagnosis of the historical disagreement

The previous registry had a live equivalent-case transaction that finalized `MAJORITY_DISAGREE`. The available receipt recorded execution status and vote metadata but did not expose private validator reasoning. Required debug methods tested against the StudioNet RPC (`gen_dbg_traceTransaction`, `gen_getTransactionReceipt`, and `gen_getTransaction`) were unavailable or returned `Method not found`. Therefore the receipt alone does not prove an `R`-versus-`M` mismatch, malformed output, adversarial uncertainty or a runtime cause.

Controlled Direct Mode reproduced a concrete failure mode: a leader and validator could independently classify the same transformation with the same substantive relation/reason but select different valid evidence paths; exact path-list equality rejected that case. The safe correction removed only the brittle exact-list comparison, retained substantive relation/reason agreement and strengthened path validation by requiring a real changed scalar. It did not add leader trust or accept arbitrary higher-severity results.

The new source was deployed as registry [`0x5f31A604e9C3A9362A01A17c5be6b8a1440Db2dF`](https://explorer-studio.genlayer.com/address/0x5f31A604e9C3A9362A01A17c5be6b8a1440Db2dF). Its live equivalent, strengthened and weakened cases all finalized with `MAJORITY_AGREE`; `R-1` closed `PASS`, and the independent recheck `R-5` also closed `PASS`. This supports the correction’s liveness benefit but does not claim unavailable private validator reasoning from the old transaction.

## Provenance categories

| Claim | Establishment |
| --- | --- |
| Input pair, policy, case order and digest | Deterministic frozen registry state |
| Target outputs | Registered target public views, strictly parsed; not off-chain truth |
| Semantic relation/reason | Leader plus independent validator GenLayer consensus |
| Evidence-path validity | Deterministic path resolution and changed-scalar checks in each execution |
| PASS/FAIL/INCONCLUSIVE | Deterministic comparator and run-closure state machine |
| Historical/current certification | Exact-bound registry views; currentness is target-manifest-version based |
| Cross-contract activation | Typed IC-to-IC public views executed and read back on stable StudioNet |
| Validator private reasoning | Not exposed by the required public receipt interface; not claimed |

## Live ambiguity

On the final registry, suite `S-4` intentionally stated that “acceptable” was undefined and did not define the relevance or direction of tone, experience, receipt, verification, day or identity. Its live run `R-4` returned `AMBIGUOUS / INSUFFICIENT_BASIS` for both cases, closed `INCONCLUSIVE`, and failed both historical and current certification. An activation consumer bound to `R-4` finalized with execution error and remained inactive.

Direct Mode and live StudioNet evidence are separate layers. Direct Mode proves controlled runtime and adversarial state-machine behaviour; live receipts prove finalized network execution and canonical state consequences.
