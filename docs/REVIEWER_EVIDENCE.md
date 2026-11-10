# Reviewer evidence ledger

This ledger separates local tests, Direct Mode, GitHub Actions and finalized
StudioNet evidence. It describes the source-matched policy-activation release
on 2026-11-10.

## Reviewer quick checklist

1. Inspect contracts/metamorph.py semantic validation and deterministic comparator.
2. Inspect contracts/policy_target.py and policy_activation.py.
3. Run npm run check:network and npm run check:live-network.
4. Run npm run check:evidence; use --full for complete transaction payloads.
5. Read the registry runs R-1 through R-5 below.
6. Verify the qualified, defective and ambiguous consumer states.
7. Compare source hashes with SOURCE_SHA256_MANIFEST.json.
8. Reproduce python -m pytest tests -q and the five-contract lint/schema commands.

## Locked environment

| Item | Verified value |
| --- | --- |
| Network | studionet |
| Chain | 61999 / 0xf22f |
| RPC | https://studio.genlayer.com/api |
| Live RPC identity | eth_chainId = 0xf22f |
| Local CLI | genlayer 0.39.1 |
| GenVM | stable v0.2.12 |
| Linter | genvm-linter 0.11.0 |
| Direct Mode package | genlayer-test 0.29.0 |
| Preview/global tooling | not used |

The live network check calls the required RPC rather than trusting the CLI
alias. The repository-local executable was used throughout.

## Local gates

| Gate | Fresh result |
| --- | --- |
| Offline tests | 39 passed |
| Direct Mode tests | 20 passed |
| Full suite | 59 passed |
| Python compilation | PASS |
| Source hashes | PASS for 5 deployable sources |
| GenVM lint | PASS for metamorph, fixture_target, fixture_consumer, policy_target and policy_activation |
| ABI/schema extraction | PASS for all five contracts |
| Live read-only evidence verifier | PASS |

Direct Mode semantic results are controlled leader/validator fixtures at the VM
boundary. They exercise response parsing, disagreement and fail-closed logic,
but they are not live validator identity evidence. The StudioNet table below is
the separate live proof.

## Current source-matched deployments

Explorer base: https://explorer-studio.genlayer.com/.

| Contract | Address | Deployment transaction |
| --- | --- | --- |
| Metamorph registry | [0x5f31A604e9C3A9362A01A17c5be6b8a1440Db2dF](https://explorer-studio.genlayer.com/address/0x5f31A604e9C3A9362A01A17c5be6b8a1440Db2dF) | [0x28bcc805dbfd8fcb0069dbcd2729a1430248e2b4f557415b00510c68c5dfb966](https://explorer-studio.genlayer.com/tx/0x28bcc805dbfd8fcb0069dbcd2729a1430248e2b4f557415b00510c68c5dfb966) |
| Stable policy target | [0x6A3fb9a5aA12A90378c9a6b98bef38e121d5B45A](https://explorer-studio.genlayer.com/address/0x6A3fb9a5aA12A90378c9a6b98bef38e121d5B45A) | [0x9bd9179826e6fba9b1966e1694837f9712729361ceefa44cc258ab9f231d76bd](https://explorer-studio.genlayer.com/tx/0x9bd9179826e6fba9b1966e1694837f9712729361ceefa44cc258ab9f231d76bd) |
| Defective policy target | [0x3F52532f59E60fa5FD3495fEc40CbbbfbBaB3705](https://explorer-studio.genlayer.com/address/0x3F52532f59E60fa5FD3495fEc40CbbbfbBaB3705) | [0xa7fd824b1738714710ebfd1f4d5487e3e8e564f5169bf4e854a7c1bf14d1bb09](https://explorer-studio.genlayer.com/tx/0xa7fd824b1738714710ebfd1f4d5487e3e8e564f5169bf4e854a7c1bf14d1bb09) |
| Qualified activation | [0x5FBf59d09daAa5512A23431cDEEEe36e3Cd77D45](https://explorer-studio.genlayer.com/address/0x5FBf59d09daAa5512A23431cDEEEe36e3Cd77D45) | [0x0f4de2c4d62afad284d129c7a387e1dcf3bf476cf4cfffe67c86bfbd08b1dd19](https://explorer-studio.genlayer.com/tx/0x0f4de2c4d62afad284d129c7a387e1dcf3bf476cf4cfffe67c86bfbd08b1dd19) |
| Defective refusal | [0xd2974957F514AD183989D9D0e7168fF69d9c4ad9](https://explorer-studio.genlayer.com/address/0xd2974957F514AD183989D9D0e7168fF69d9c4ad9) | [0xcf08747ca1952ef92e3b7665af66814205999cc3065dff70c338dbef3ea97010](https://explorer-studio.genlayer.com/tx/0xcf08747ca1952ef92e3b7665af66814205999cc3065dff70c338dbef3ea97010) |
| Ambiguous refusal | [0x3D1d346E55f2D44322912bc2A2A0CD9Ce38Ae849](https://explorer-studio.genlayer.com/address/0x3D1d346E55f2D44322912bc2A2A0CD9Ce38Ae849) | [0xae4e44c70d30529766052a3d570950861faee0fd466b1fd60ec7a8c04cec2371](https://explorer-studio.genlayer.com/tx/0xae4e44c70d30529766052a3d570950861faee0fd466b1fd60ec7a8c04cec2371) |

All listed deployment transactions finalized with successful execution. The
registry deployment was the source-hardening build; the earlier registry and
fixture/consumer addresses remain superseded historical deployments.

## Registry lifecycle

The current registry readback is targets=2, suites=4, cases=10, runs=5.

| Run | Suite / target | Frozen digest | Readback |
| --- | --- | --- | --- |
| R-1 | S-1 / T-1 stable | 730f081a66c7b64b9c3e727885ba20d0fc39b7a4fb070bd4aa88db06b4d115b2 | PASS; 3 passes; historical=true; current=true |
| R-2 | S-2 / T-2 defective | 32b2a8737b09f6bfa4f34ed818ab0000a216f732e2512dea554c4125319e3d6d | FAIL; one failed equivalent case; certified=false |
| R-3 | S-3 / T-1 invalid | 3791bf01bf77c4c614a63f0d453523222ce37cba3746a5d6aadfec3c5d15fb4b | INCONCLUSIVE; missing receipt was INVALID / MATERIAL_DIFFERENCE |
| R-4 | S-4 / T-1 ambiguous | 2c551540df49ae4dedcfcad55b51975b44379c1b07ad5906621e47938524fe7c | INCONCLUSIVE; both cases AMBIGUOUS / INSUFFICIENT_BASIS |
| R-5 | S-1 / T-1 recheck | 730f081a66c7b64b9c3e727885ba20d0fc39b7a4fb070bd4aa88db06b4d115b2 | PASS; distinct tester; R-1 preserved |

S-1 contains an equivalent tone change, a strengthened experience change and a
weakened experience change. The stable target passes all three. S-2 uses the
same shape against the intentionally defective target; its valid equivalent
case observes ALLOW to DENY, so deterministic comparison produces FAIL.

S-3 demonstrates that a materially missing signed receipt cannot be relabeled
cosmetic. S-4 freezes intentionally underspecified policy text; live semantic
readback was AMBIGUOUS and the run could not certify.

## Consequential policy activation

The qualified activation consumer is immutably bound to:

- registry 0x5f31A604e9C3A9362A01A17c5be6b8a1440Db2dF
- target T-1 and candidate 0x6A3fb9a5aA12A90378c9a6b98bef38e121d5B45A
- suite S-1 and digest 730f081a66c7b64b9c3e727885ba20d0fc39b7a4fb070bd4aa88db06b4d115b2
- expected run R-1
- policy id/version eligibility-policy-v1
- policy digest 49b4c5b2dac5e9fc9ed6eb1ad86dbbf9559de533629892d0e9632a5f2526c5b3
- one authorized activation actor

The contract obtains is_certified_current from the real deployed registry and
also checks the target record and policy manifest. The unauthorized activation
transaction [0x6f2d7469d86a6fae10a910f17744a773ffa1a849eb8570a2c6cba4283ee0c756](https://explorer-studio.genlayer.com/tx/0x6f2d7469d86a6fae10a910f17744a773ffa1a849eb8570a2c6cba4283ee0c756)
left the consumer inactive. Authorized activation
[0xb559f7e882b9d18f6e4ba4fe34b58377222238f10f7998b80d0c4a42ac4546a6](https://explorer-studio.genlayer.com/tx/0xb559f7e882b9d18f6e4ba4fe34b58377222238f10f7998b80d0c4a42ac4546a6)
set activated=true and run_id=R-1.

The downstream authorization
[0xde8dcdf529bd2f2160bcaa65ef92b9bcbf0554dc744a7e94297a2cfaedb476df](https://explorer-studio.genlayer.com/tx/0xde8dcdf529bd2f2160bcaa65ef92b9bcbf0554dc744a7e94297a2cfaedb476df)
recorded one ALLOW result with score 6500. A denied request
[0xbf417961ff591afdfb3d5415fbf78b194875d647d136c79a829a94978548a0ca](https://explorer-studio.genlayer.com/tx/0xbf417961ff591afdfb3d5415fbf78b194875d647d136c79a829a94978548a0ca)
did not increment the count. Replay
[0x539ca0ac1e520445832ba2f138820069f163a24f6a1854179828fdc5c3b0df30](https://explorer-studio.genlayer.com/tx/0x539ca0ac1e520445832ba2f138820069f163a24f6a1854179828fdc5c3b0df30)
was rejected and the count remained one. The defective and ambiguous consumers
remain inactive after their activation attempts.

## Consensus and security evidence

The primary correction is evidence-path hardening. The leader and validator
still independently classify the frozen policy and input pair, and the contract
compares only the substantive relation and reason code rather than brittle raw
explanations or exact path-list equality. A result is accepted only when its
paths are real scalar paths, include paired original/variant references, and
include an observed changed scalar. This blocks a leader that cites only
unchanged or irrelevant fields while preserving the liveness correction that
avoided exact path-list comparison.

Direct Mode regressions cover hidden prerequisites, mixed-direction changes,
different subjects, prompt injection, malicious leader classifications,
validator disagreement, fabricated/irrelevant paths, duplicate/missing paths
and malformed semantic outputs. The target outputs are never passed to the
semantic classifier.

The deterministic comparator alone decides PASS/FAIL after semantic VALID:
EQUIVALENT requires equal decisions and bounded score delta; STRENGTHENED
requires non-decreasing rank and score; WEAKENED requires non-increasing rank
and score. INVALID or AMBIGUOUS always produce INCONCLUSIVE and cannot certify.

## Source integrity and receipts

The source manifest is SOURCE_SHA256_MANIFEST.json. It records canonical Git
hashes and raw deployed-byte hashes retrieved through genlayer-js
getContractCode. The source contract commit is a0300f1; later evidence-only
changes do not change the five contract bytes.

| File | Canonical hash | Deployed raw hash |
| --- | --- | --- |
| contracts/metamorph.py | 9c5514ebfa0bad0c4cb66e7768293b590688c32314c0d7c97d32c7d9dd4a2fab | c09d84d736ef27baa85101f69b650bbc079407954148aaff37254ec4e296445b |
| contracts/fixture_target.py | bfa60b53a4750b27e71d65ff29d13e443f1fb4cf9449c704fe2edcc977bd61f4 | ad4d29a90fa21ca561cb9a92be5da490bb6f5fe086b50015ab6f0e66a0343906 |
| contracts/fixture_consumer.py | e866cddd0fccbd6f0049c7c4bc45e308b4134337c7fa1e7dda7ed4c330dd766d | 5c3dd7f2aab514d5668dfd8f6d9f24f17e28c44c079cb599bffaa6d2e05b424d |
| contracts/policy_target.py | 5ae0fef2acb3026a4100777aeda97061b5d08815706984ddfc4e9d502a071bdd | same |
| contracts/policy_activation.py | 6de5f8fd52562279b5ef7b0e95778ba1421c3597e32feb3133c4a3885835bee3 | same |

A read-only evidence script runs through the required RPC, checks chain identity,
reads every configured run and consumer, retrieves every listed source and
checks every transaction hash. It reports unsupported historical transaction
indexing as a warning and fails only contradicted mandatory claims. One
historical add_case write for C-5 was not recoverable as a transaction hash;
C-5 and its resulting suite/run state remain readable and are not replaced by
an unrelated hash. Use:

    npm run check:evidence
    npm run check:evidence -- --full

GitHub Actions and the final commit URL are updated in the release report after
the normal push.
