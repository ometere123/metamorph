# Metamorph threat model

## Protected properties

Metamorph protects the integrity of a frozen metamorphic test definition, the provenance of captured target outputs, deterministic PASS/FAIL calculation, exact-bound certification and one-time downstream activation. It does not prove that a target's decision is objectively correct or that the target's declared version identifies immutable bytecode.

## Actors and trust boundaries

- **Target registrant:** binds a public target address and its adapter manifest to a registry record.
- **Suite curator:** chooses the frozen policy, names the case author and freezes the ordered case digest.
- **Case author:** supplies the transformation cases before freezing.
- **Independent tester:** captures target public views, requests semantic evaluation and closes a run. A recheck must use a different tester address.
- **Target contract:** supplies adapter responses. It may be dishonest or deliberately defective; Metamorph treats its response as an observation, not ground truth.
- **GenLayer leader and validators:** independently assess only whether the frozen transformation is semantically valid. They are not trusted as a single authority.
- **Consumer:** binds an exact registry, suite, target and digest and asks the current certification view before its irreversible action.

Distinct addresses establish protocol role separation, not guaranteed real-world independence between wallet controllers. There is no administrator override or hidden privileged write path.

## Main threats and controls

| Threat | Control |
| --- | --- |
| Curator or author rewrites a frozen policy/case | Frozen suites reject edits; ordered cases and target binding are in the digest. |
| Tester substitutes outputs or cases | Captures call the registered target's two public views; snapshots bind run, case, target, version, suite/case digests and tester. Strict adapter output validation rejects malformed data. |
| Target changes after registration | Run opening and capture recheck the public manifest version. Current certification rechecks it again. This is version-based, not bytecode attestation. |
| Malicious leader fabricates semantic result | Validator independently runs the semantic prompt; strict schema, real scalar path, paired-path and relation/reason checks fail closed. |
| Malformed, injected or oversized case data | Duplicate JSON keys, non-finite values, excessive depth/nodes/list size, control bytes, oversized inputs and malformed output are rejected. Retrieved policy/input text is untrusted data. |
| Evidence-path forgery or path disagreement | Paths must resolve to real scalar leaves, include both sides and use paired suffixes. Exact path-list equality is deliberately not required because it caused a reproduced liveness failure; substantive relation/reason agreement remains required. |
| Semantic ambiguity becomes a target failure | Only `VALID` reaches the deterministic comparator. `INVALID` and `AMBIGUOUS` become `INCONCLUSIVE` and cannot certify. |
| Comparator is replaced by model prose | PASS/FAIL is computed deterministically from strict decision/score outputs and the frozen relation. |
| Cross-suite/run/digest confusion | IDs, target IDs, suite digests, case digests, target addresses and versions are checked at every lifecycle boundary. Consumer uses exact current certification arguments. |
| Recheck overwrites history | Runs are append-only; parent runs must be closed and rechecks use a different tester. |
| Consumer replay | Consumer stores `activated` and `used_run`; activation is irreversible and second calls fail. |
| Consumer binding mismatch | Constructor uses a typed `Address`; the current view checks registry, suite, target and exact digest. A correctly bound FAIL consumer was tested live. |
| Preview-network or global-CLI deployment | Repository-local CLI, configuration guard and live `eth_chainId` gate require stable StudioNet 61999. |

## Residual risks

1. A malicious target can lie through its own adapter, return context-dependent values or report a false version. Metamorph only certifies the observed public-view relationship.
2. A target-declared version string is not a cryptographic code identity. This release verified exact source bytes for the listed deployments with `genlayer-js getContractCode`, but future target upgrades need a new registration/run and consumers still rely on the target's current manifest semantics.
3. LLM semantic judgments can be wrong or disagree. The protocol bounds the result, requires independent validator recomputation and fails closed, but it cannot make semantic interpretation infallible.
4. Role addresses can be controlled by one real-world actor. The contract cannot establish social independence.
5. StudioNet receipts expose execution outcomes and validator votes but not private model reasoning. Direct Mode adversarial cases therefore supplement, rather than replace, live consensus evidence.
6. Public policies, inputs, outputs and digests are readable on-chain; users must not include secrets or personal data.

