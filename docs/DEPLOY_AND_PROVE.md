# Deploy and prove Metamorph

This runbook records the source-matched release and the exact commands used to
verify it. It is limited to stable StudioNet: network studionet, chain 61999 /
0xf22f, RPC https://studio.genlayer.com/api, repository-local genlayer 0.39.1,
stable GenVM v0.2.12, genvm-linter 0.11.0 and genlayer-test 0.29.0.

## 1. Reproduce the locked environment

From the repository root:

    npm ci --ignore-scripts --no-audit --no-fund
    python -m pip install -r requirements-dev.txt
    npm exec -- genlayer network set studionet
    npm run check:network
    npm run check:live-network
    npm exec -- genlayer --version

The live guard independently calls eth_chainId on the required RPC and requires
0xf22f. No global GenLayer executable or preview network is part of this
release.

## 2. Local verification recorded for this release

The final local run on 2026-11-10 recorded:

| Gate | Result |
| --- | --- |
| python -m pytest tests/offline -q | 39 passed |
| python -m pytest tests/direct -q | 20 passed |
| python -m pytest tests -q | 59 passed |
| python -m compileall -q contracts tests | PASS |
| python scripts/verify_source_hashes.py | PASS, 5 deployable sources |
| npm run check:network | PASS, studionet / 61999 / local 0.39.1 |
| npm run check:live-network | PASS, live eth_chainId=0xf22f |
| GenVM lint | PASS for all five contracts, stable v0.2.12 |
| ABI/schema extraction | PASS for all five contracts |
| npm run check:evidence | PASS; no contradicted state/source claims |

Direct Mode uses controlled VM-boundary adapters and model-response fixtures; it
is not represented as live validator identity evidence. Live consensus and
cross-contract results are listed separately below.

## 3. Source-matched live deployments

Explorer base: https://explorer-studio.genlayer.com/.

| Contract | Address | Deployment transaction | Result |
| --- | --- | --- | --- |
| Metamorph registry | [0x5f31A604e9C3A9362A01A17c5be6b8a1440Db2dF](https://explorer-studio.genlayer.com/address/0x5f31A604e9C3A9362A01A17c5be6b8a1440Db2dF) | [0x28bcc805dbfd8fcb0069dbcd2729a1430248e2b4f557415b00510c68c5dfb966](https://explorer-studio.genlayer.com/tx/0x28bcc805dbfd8fcb0069dbcd2729a1430248e2b4f557415b00510c68c5dfb966) | FINALIZED; MAJORITY_AGREE; leader execution SUCCESS |
| Stable policy target | [0x6A3fb9a5aA12A90378c9a6b98bef38e121d5B45A](https://explorer-studio.genlayer.com/address/0x6A3fb9a5aA12A90378c9a6b98bef38e121d5B45A) | [0x9bd9179826e6fba9b1966e1694837f9712729361ceefa44cc258ab9f231d76bd](https://explorer-studio.genlayer.com/tx/0x9bd9179826e6fba9b1966e1694837f9712729361ceefa44cc258ab9f231d76bd) | FINALIZED; execution SUCCESS |
| Defective policy target | [0x3F52532f59E60fa5FD3495fEc40CbbbfbBaB3705](https://explorer-studio.genlayer.com/address/0x3F52532f59E60fa5FD3495fEc40CbbbfbBaB3705) | [0xa7fd824b1738714710ebfd1f4d5487e3e8e564f5169bf4e854a7c1bf14d1bb09](https://explorer-studio.genlayer.com/tx/0xa7fd824b1738714710ebfd1f4d5487e3e8e564f5169bf4e854a7c1bf14d1bb09) | FINALIZED; execution SUCCESS; inconsistent=true |
| Qualified policy activation | [0x5FBf59d09daAa5512A23431cDEEEe36e3Cd77D45](https://explorer-studio.genlayer.com/address/0x5FBf59d09daAa5512A23431cDEEEe36e3Cd77D45) | [0x0f4de2c4d62afad284d129c7a387e1dcf3bf476cf4cfffe67c86bfbd08b1dd19](https://explorer-studio.genlayer.com/tx/0x0f4de2c4d62afad284d129c7a387e1dcf3bf476cf4cfffe67c86bfbd08b1dd19) | FINALIZED; execution SUCCESS |
| Defective-candidate refusal | [0xd2974957F514AD183989D9D0e7168fF69d9c4ad9](https://explorer-studio.genlayer.com/address/0xd2974957F514AD183989D9D0e7168fF69d9c4ad9) | [0xcf08747ca1952ef92e3b7665af66814205999cc3065dff70c338dbef3ea97010](https://explorer-studio.genlayer.com/tx/0xcf08747ca1952ef92e3b7665af66814205999cc3065dff70c338dbef3ea97010) | FINALIZED; remains inactive |
| Ambiguous-candidate refusal | [0x3D1d346E55f2D44322912bc2A2A0CD9Ce38Ae849](https://explorer-studio.genlayer.com/address/0x3D1d346E55f2D44322912bc2A2A0CD9Ce38Ae849) | [0xae4e44c70d30529766052a3d570950861faee0fd466b1fd60ec7a8c04cec2371](https://explorer-studio.genlayer.com/tx/0xae4e44c70d30529766052a3d570950861faee0fd466b1fd60ec7a8c04cec2371) | FINALIZED; remains inactive |

The earlier registry and fixture/consumer deployments remain as historical
evidence. They are not the current integration registry. The source-matched
current registry is the first row.

## 4. Exact policy-activation binding

The qualified activation contract was constructed with typed GenLayer Address
arguments and these exact values:

    registry:              0x5f31A604e9C3A9362A01A17c5be6b8a1440Db2dF
    target_id:              T-1
    suite_id:               S-1
    suite_digest:           730f081a66c7b64b9c3e727885ba20d0fc39b7a4fb070bd4aa88db06b4d115b2
    expected_run_id:        R-1
    candidate:              0x6A3fb9a5aA12A90378c9a6b98bef38e121d5B45A
    policy_id:              eligibility-policy-v1
    policy_version:         eligibility-policy-v1
    policy_digest:          49b4c5b2dac5e9fc9ed6eb1ad86dbbf9559de533629892d0e9632a5f2526c5b3
    authorized_activator:   deployment/test activator address

The defective candidate uses the same binding shape with target T-2, suite S-2,
run R-2 and policy digest
3b93fa93d4fc740d1c5ee7b1dba1ff0b9cd3d7e1c0289af5d0dee042af6fefe4. The
ambiguous refusal binds run R-4. The authorized actor is not printed because
it is not needed for read-only verification.

## 5. Live lifecycle evidence

The current registry readback is targets=2, suites=4, cases=10, runs=5.

| Run | Meaning | Final state |
| --- | --- | --- |
| R-1 / S-1 / T-1 | Stable candidate | PASS, 3/3 cases, historical and current certification true |
| R-2 / S-2 / T-2 | Defective candidate | FAIL, 1 failed equivalent case and 2 passes, certification false |
| R-3 / S-3 / T-1 | Missing signed receipt claimed equivalent | INCONCLUSIVE; INVALID / MATERIAL_DIFFERENCE |
| R-4 / S-4 / T-1 | Underspecified policy | INCONCLUSIVE; AMBIGUOUS / INSUFFICIENT_BASIS |
| R-5 / S-1 / T-1 | Independent recheck of R-1 | PASS; different tester; parent R-1 unchanged |

The stable policy requires a weekday, verified=true, signed_receipt=true and at
least four years of experience. tone is declared cosmetic. The defective
candidate makes urgent tone deny an otherwise eligible input. The valid
equivalent case therefore produces deterministic ALLOW -> DENY and the run
fails without allowing a claimed semantic relation to write PASS.

The live-policy transaction set, readbacks and explorer links are in
scripts/live_evidence_config.json. The read-only verifier checks every
configured run, both certification predicates, all three activation states,
every listed deployed source and all 60 recorded transaction hashes:

    npm run check:evidence
    npm run check:evidence -- --full

The default command prints compact transaction/receipt summaries. --full prints
complete payloads. The verifier never writes and never requires a wallet.
Missing historical transaction indexing is a warning; contradicted chain
identity, state, or source claims are failures.

Key state-transition transactions:

| Action | Transaction |
| --- | --- |
| Unauthorized activation rejected | [0x6f2d7469d86a6fae10a910f17744a773ffa1a849eb8570a2c6cba4283ee0c756](https://explorer-studio.genlayer.com/tx/0x6f2d7469d86a6fae10a910f17744a773ffa1a849eb8570a2c6cba4283ee0c756) |
| Authorized R-1 activation | [0xb559f7e882b9d18f6e4ba4fe34b58377222238f10f7998b80d0c4a42ac4546a6](https://explorer-studio.genlayer.com/tx/0xb559f7e882b9d18f6e4ba4fe34b58377222238f10f7998b80d0c4a42ac4546a6) |
| Downstream ALLOW authorization | [0xde8dcdf529bd2f2160bcaa65ef92b9bcbf0554dc744a7e94297a2cfaedb476df](https://explorer-studio.genlayer.com/tx/0xde8dcdf529bd2f2160bcaa65ef92b9bcbf0554dc744a7e94297a2cfaedb476df) |
| Replay rejected | [0x539ca0ac1e520445832ba2f138820069f163a24f6a1854179828fdc5c3b0df30](https://explorer-studio.genlayer.com/tx/0x539ca0ac1e520445832ba2f138820069f163a24f6a1854179828fdc5c3b0df30) |
| Denied downstream request rejected | [0xbf417961ff591afdfb3d5415fbf78b194875d647d136c79a829a94978548a0ca](https://explorer-studio.genlayer.com/tx/0xbf417961ff591afdfb3d5415fbf78b194875d647d136c79a829a94978548a0ca) |
| Defective activation refusal | [0xef0cb0323620b551c37e9b0131ef2aa9b720a4aefc970817ac96c17e6c4bb1e4](https://explorer-studio.genlayer.com/tx/0xef0cb0323620b551c37e9b0131ef2aa9b720a4aefc970817ac96c17e6c4bb1e4) |
| Ambiguous activation refusal | [0x3e789cb4f2fdf1061315514a4c78cb2ef5f57dcff3203604ba7de971a6e3dc8a](https://explorer-studio.genlayer.com/tx/0x3e789cb4f2fdf1061315514a4c78cb2ef5f57dcff3203604ba7de971a6e3dc8a) |

Rejected operations are not presented as successful execution. Their final
receipts are retained in the read-only ledger, and unchanged contract
readbacks are the state proof.

## 6. Source integrity

SOURCE_SHA256_MANIFEST.json records canonical Git hashes and raw deployed
hashes. The current source commit for the five deployable contracts is a0300f1;
evidence-only documentation/tooling commits do not change those contract bytes.

| File | Canonical SHA-256 | Raw deployed SHA-256 |
| --- | --- | --- |
| contracts/metamorph.py | 9c5514ebfa0bad0c4cb66e7768293b590688c32314c0d7c97d32c7d9dd4a2fab | c09d84d736ef27baa85101f69b650bbc079407954148aaff37254ec4e296445b |
| contracts/fixture_target.py | bfa60b53a4750b27e71d65ff29d13e443f1fb4cf9449c704fe2edcc977bd61f4 | ad4d29a90fa21ca561cb9a92be5da490bb6f5fe086b50015ab6f0e66a0343906 |
| contracts/fixture_consumer.py | e866cddd0fccbd6f0049c7c4bc45e308b4134337c7fa1e7dda7ed4c330dd766d | 5c3dd7f2aab514d5668dfd8f6d9f24f17e28c44c079cb599bffaa6d2e05b424d |
| contracts/policy_target.py | 5ae0fef2acb3026a4100777aeda97061b5d08815706984ddfc4e9d502a071bdd | same |
| contracts/policy_activation.py | 6de5f8fd52562279b5ef7b0e95778ba1421c3597e32feb3133c4a3885835bee3 | same |

The verifier retrieves deployed source through genlayer-js getContractCode and
compares raw deployed bytes separately from canonical LF-normalized Git hashes.
This is source retrieval evidence for the listed addresses; a target's
self-declared version remains a distinct, non-cryptographic currentness input.

## 7. Operational security

scripts/studionet_ops.mjs now requires an interactive TTY for keystore password
entry, disables echo, masks input, refuses non-TTY password reads and never
prints the password or decrypted wallet material. The deploy operation reads
only a repository-contained contract path and reports a failed finalized
execution as ok=false even when a transaction hash exists. No keystore,
private key, mnemonic or environment secret is committed.

The transaction ledger cannot restore history that the required RPC no longer
indexes. One historical add_case write for C-5 was not recoverable as a
transaction hash; the case, suite digest, run and final state are independently
readable. This is recorded as an evidence limitation, not replaced with an
unrelated hash.
