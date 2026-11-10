# Metamorph consensus design

Metamorph uses GenLayer semantic consensus for one narrow question: does a frozen pair of input objects satisfy the frozen policy and the claimed metamorphic relation? It does not ask a model to decide whether a target is correct and it never gives the model the target's observed outputs as justification.

## Execution boundary

`evaluate_case` constructs one bounded prompt from the frozen policy, case relation, transformation note and the two frozen input objects. The input objects are delimited as untrusted data. The leader calls `gl.nondet.exec_prompt(..., response_format="json")`; `gl.vm.run_nondet_unsafe` then gives the leader result to a validator. The validator independently calls the same semantic prompt and validates its own result before comparing the bounded semantic signature.

The accepted semantic schema is exact:

```json
{
  "relation": "VALID | INVALID | AMBIGUOUS",
  "reason_code": "RELATION_SATISFIED | MATERIAL_DIFFERENCE | INSUFFICIENT_BASIS",
  "evidence_paths": ["original.some_scalar", "variant.some_scalar"]
}
```

The contract rejects extra or missing keys, unknown enums, contradictory reason codes, non-scalar or invented paths, duplicate paths, malformed JSON, oversized responses and unpaired original/variant path suffixes. Evidence paths are provenance for the independent semantic conclusion; they are not accepted as a substitute for semantic recomputation.

The validator compares the leader and its independent conclusion on `relation` and `reason_code`. It does not require identical prose or identical path selection, because two independently reasoned validators can select different valid paired facts. Requiring the exact path list was the reproducible liveness defect in the earlier implementation: a valid equivalent transformation could be rejected when the models selected different but real paths. The correction preserves strict path validity and pairing while avoiding that unsafe overconstraint.

## Deterministic boundary

Only `VALID` reaches the deterministic comparator. `INVALID` and `AMBIGUOUS` become `INCONCLUSIVE`; neither can manufacture a target failure or pass. For `VALID` cases the contract compares the two strictly validated target adapter outputs:

- `EQUIVALENT`: identical decision and absolute score delta within the frozen tolerance.
- `STRENGTHENED`: decision rank and score do not decrease.
- `WEAKENED`: decision rank and score do not increase.

The target's output is constrained to the adapter schema and `score_bps` range `0..10000`. The model cannot write the final PASS/FAIL value.

## Prompt-injection boundary

Policy text, transformation notes, original inputs and variant inputs are untrusted case data. Strings such as “ignore previous instructions” remain data and are not executed. Strict bounds and schema checks are defense in depth; semantic safety still depends on independent validators correctly interpreting the frozen policy. The target's outputs are deliberately omitted from the semantic prompt to prevent outcome-driven rationalization.

## Observed diagnosis and correction

The first live registry deployment (now superseded) produced a finalized `MAJORITY_DISAGREE` on one equivalent-case evaluation. Available receipts showed successful leader/validator VM executions but did not expose the validators' semantic reasoning. The required debug RPC methods tested (`gen_dbg_traceTransaction`, `gen_getTransactionReceipt`, and `gen_getTransaction`) returned `Method not found`; therefore no exact validator conclusion is claimed.

The diagnosis was treated as a hypothesis until controlled Direct Mode tests reproduced the failure mode: exact equality of evidence-path lists rejects a leader and validator that agree on relation/reason but choose different valid paired paths. The corrected source compares the substantive semantic signature and still rejects forged, nonexistent, crossed, duplicate or unpaired paths. A single corrected live equivalent case then finalized `MAJORITY_AGREE`, stored `VALID / RELATION_SATISFIED`, and produced deterministic `PASS` on the final registry. This is evidence that the correction removed the reproduced liveness problem; it is not a claim that the unavailable old validator traces proved one unique internal cause.

## What is and is not proven

Direct Mode tests exercise the pinned GenVM runner with controlled mock model responses, including malicious leaders, disagreement, prompt injection and malformed outputs. They are not live validator identities. The final StudioNet receipts prove finalized network execution, leader/validator execution status and state consequences; the platform receipt does not expose private model reasoning. The live invalid suite provides an on-chain `INVALID / MATERIAL_DIFFERENCE` and `INCONCLUSIVE` result, while the defective fixture provides a live `VALID` semantic classification followed by deterministic `FAIL`.

