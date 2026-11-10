# Metamorph verification ledger

This ledger separates local tests, Direct Mode, GitHub CI and finalized StudioNet evidence. Values below were recorded from the final registry deployment and its source-matched fixtures/consumers on 2026-11-10. The earlier registry `0x746ea06755af60d06DEe75993c9dE75fD6336cE9` is retained only as superseded historical evidence; it is not the release registry.

## Locked environment

| Item | Verified result | Evidence |
| --- | --- | --- |
| Network | `studionet` | Repository-local CLI network guard |
| Chain | `61999` / `0xf22f` | Live `eth_chainId` from the required RPC |
| RPC | `https://studio.genlayer.com/api` | `npm run check:live-network` |
| CLI | `genlayer@0.39.1` | `node_modules/.bin/genlayer(.cmd) --version` |
| GenVM bundle | `v0.2.12` | linter download and Direct Mode configuration |
| Linter | `genvm-linter 0.11.0` | three contracts checked and three schemas extracted |
| Python test package | `genlayer-test 0.29.0` | pinned requirements and test run |
| Preview network/global CLI | Not used | no `61997`, `studio-dev`, `studio-next` or global CLI invocation |

## Local verification

| Gate | Result |
| --- | --- |
| `python -m pytest tests/offline -q` | **36 passed** |
| `python -m pytest tests/direct -q` | **15 passed** |
| `python -m pytest tests -q` | **51 passed** |
| `python -m compileall -q contracts tests` | **PASS** |
| `npm run check:network` | **PASS** |
| `npm run check:live-network` | **PASS**, live `eth_chainId=0xf22f` |
| GenVM lint | **PASS**, all three contracts, 3/3 lint checks each |
| ABI/schema extraction | **PASS**, all three contracts |

Direct Mode uses controlled VM-boundary adapters and mocked semantic responses. It is not a claim that those tests are live StudioNet validator identities. The live receipts below are the separate network evidence.

## Final deployed contracts

Explorer pages use the official StudioNet explorer: [`explorer-studio.genlayer.com`](https://explorer-studio.genlayer.com/). Each linked transaction was checked for HTTP availability and each receipt was independently polled to `FINALIZED` with the execution result recorded.

| Contract | Address | Deployment transaction | Final result |
| --- | --- | --- | --- |
| Stable target fixture | [`0xE763C529…607C22`](https://explorer-studio.genlayer.com/address/0xE763C5294ea266D2C17106fFd6d5136A6d607C22) | [`0x76f717…cb7d49`](https://explorer-studio.genlayer.com/tx/0x76f717481f6eb37e6d5105dd81770121840e1a72be31752faafa8d4ad1cb7d49) | `FINALIZED`, `MAJORITY_AGREE`, execution `SUCCESS` |
| Defective target fixture | [`0x286345Cc…cfA354`](https://explorer-studio.genlayer.com/address/0x286345CcD4A86560e8F97D1Fe2bc140724cfA354) | [`0xe6492e…a34a92`](https://explorer-studio.genlayer.com/tx/0xe6492eab68d8878fd3769554af18263b68fdab215c5391f810c71d140ca34a92) | `FINALIZED`, `MAJORITY_AGREE`, execution `SUCCESS` |
| **Final Metamorph registry** | [`0x4a7F6a37…5aFA8b`](https://explorer-studio.genlayer.com/address/0x4a7F6a372d3A686302d1c4f5f162386Ab85aFA8b) | [`0x02aebf…2868ce8`](https://explorer-studio.genlayer.com/tx/0x02aebfe82ccbf12c9ec2956cc1f331a1daa72afb4553731a0bf78e2342868ce8) | `FINALIZED`, `MAJORITY_AGREE`, execution `SUCCESS` |
| **Primary consumer, stable PASS binding** | [`0x94312d8d…cf12e`](https://explorer-studio.genlayer.com/address/0x94312d8de2282485A939953E93De097FD2acf12e) | [`0x293a8d…d4fa0`](https://explorer-studio.genlayer.com/tx/0x293a8d51cd2e7091066afbebe939a7c7bf77419002479347080032adae1d4fa0) | `FINALIZED`, `MAJORITY_AGREE`, execution `SUCCESS` |
| Negative consumer, defective FAIL binding | [`0x3EFCF9fb…Cc440b`](https://explorer-studio.genlayer.com/address/0x3EFCF9fb9Ce7946db998DA2ee28E026b85Cc440b) | [`0xc5b0c9…f5daed`](https://explorer-studio.genlayer.com/tx/0xc5b0c9770f725b32ee0973ab6d8df0a749aa3627c18350c33a9769276df5daed) | `FINALIZED`, `MAJORITY_AGREE`, execution `SUCCESS` |

The final registry source was deployed after the evidence-path consensus correction. Its exact source is commit `5f6d2e0`; the earlier registry deployment at `0x746ea06755af60d06DEe75993c9dE75fD6336cE9` used the superseded source and must not be used for current proofs.

## Adapter readbacks and source parity

The stable fixture returned manifest `{"schema":"metamorph.adapter/1","version":"fixture-v1-stable"}` and both neutral/urgent inputs returned `ALLOW / 6000`. The defective fixture returned `fixture-v1-broken`; the same neutral input returned `ALLOW / 6000` while urgent returned `DENY / 0`.

`genlayer-js getContractCode` over the required RPC returned exact byte-for-byte matches for every final deployment:

| Source | Git-blob SHA-256 | Deployed raw SHA-256 | Retrieved bytes | Deployment(s) |
| --- | --- | --- | ---: | --- |
| `contracts/metamorph.py` | `48febe775104155aac5ded814db6e417be1646221a4d117f7683ac5e6106bf3e` | `fbe31d0483ed2f331917c78dc78c9e38c26099649a539ee4cc3e73fada68e355` | 25,563 | final registry |
| `contracts/fixture_target.py` | `bfa60b53a4750b27e71d65ff29d13e443f1fb4cf9449c704fe2edcc977bd61f4` | `ad4d29a90fa21ca561cb9a92be5da490bb6f5fe086b50015ab6f0e66a0343906` | 1,639 | stable and defective fixtures |
| `contracts/fixture_consumer.py` | `e866cddd0fccbd6f0049c7c4bc45e308b4134337c7fa1e7dda7ed4c330dd766d` | `5c3dd7f2aab514d5668dfd8f6d9f24f17e28c44c079cb599bffaa6d2e05b424d` | 1,747 | both consumers |

The manifest is [`SOURCE_SHA256_MANIFEST.json`](../SOURCE_SHA256_MANIFEST.json). Constructor configuration, not source bytes, distinguishes stable and defective fixture behaviour.

## Final registry lifecycle

All successful writes in this table finalized with `MAJORITY_AGREE` and successful leader execution. Rejection controls finalized with `MAJORITY_AGREE` but leader/validator execution `ERROR`, and their state readbacks remained unchanged.

### Registration, suites and freezing

| Action | Finalized transaction | Readback |
| --- | --- | --- |
| Register stable target `T-1` | [`0x40e334…ffad769`](https://explorer-studio.genlayer.com/tx/0x40e33419d3fcb92c641d8cc9a8b7c0b83fd208fb49818b75b9ad53fefffad769) | address `0xe763…7c22`, version `fixture-v1-stable`, registrant recorded |
| Register defective target `T-2` | [`0xbfccb7…2efae0`](https://explorer-studio.genlayer.com/tx/0xbfccb733dea05ab083cf50c71ccb80be87ab3b538f72595e1a711e4bdf2efae0) | address `0x2863…a354`, version `fixture-v1-broken`, registrant recorded |
| Create stable suite `S-1` | [`0x7ee876…10b7aa`](https://explorer-studio.genlayer.com/tx/0x7ee876b7f022ad7b2931a37af4e9b46172e808fd9f29a616ed2ebecff6110b7aa) | target `T-1`, distinct curator and author |
| Create defective suite `S-2` | [`0x4650ca…2e1c39`](https://explorer-studio.genlayer.com/tx/0x4650ca335a206c40ffeb82254983ab363e1bcd5c06f8c195f03f6bf85e2e1c39) | target `T-2`, distinct curator and author |
| Freeze `S-1` | [`0xdff14d…404eb3`](https://explorer-studio.genlayer.com/tx/0xdff14daf56dcae85a7e325ca8f1a0bd6162e0b7e1cc1ad8083fba4998f4404eb3) | digest `299da4c043615d7ef372903d7ff979577e69182e0fbda648a6ac075ee02a6848`, cases `C-1,C-2` |
| Freeze `S-2` | [`0x770f08…937212`](https://explorer-studio.genlayer.com/tx/0x770f08663b94f695848ae01ec2430c11a32428da9db7f395b2278243209937212) | digest `88c0efd006eefe4cf14ccfe956b3d8227a86e9a7fd6893b028085260c9556bb7`, cases `C-3,C-4` |
| Create/freeze invalid suite `S-3` | [`0xcc7c70…61ca74`](https://explorer-studio.genlayer.com/tx/0xcc7c7058f3326c185a5535b5a6ff51cbb187812f2cfec6611928fb8272661ca74) | digest `a3a39b78bb17eb020bb7e378b0688cd4684eae4b93b4081e618c8f26616b9e3d`, cases `C-5,C-6` |
| Post-freeze mutation attempt | [`0x57d120…e9b55b`](https://explorer-studio.genlayer.com/tx/0x57d120772537899d4fd956d267e4e86f4283a1e89da3d2c8dd6a667c48ee9b55b) | finalized execution `ERROR`; frozen suite unchanged |

## Live semantic runs

| Run | Open / capture / evaluate / close | Final on-chain result |
| --- | --- | --- |
| Stable `R-1` | open [`0xc44b…0c8ba5`](https://explorer-studio.genlayer.com/tx/0xc44b685820fff52b4bff57aae6227e64bba8639d66ec73b811cec8ae1c00c8ba5); captures [`C-1`](https://explorer-studio.genlayer.com/tx/0xe57c86866750ba279da5de4bdc3c15bc5c8f226051f8c7ccc365c0908655275c), [`C-2`](https://explorer-studio.genlayer.com/tx/0xb367263941a872dc14286019c175d957f21dea7f4a57ae2618e9141540559c93c); evaluates [`C-1`](https://explorer-studio.genlayer.com/tx/0xf10cb4f0042282ccacc2e99ddd244773c39c7ae94c06edee42a5272eae554c18b), [`C-2`](https://explorer-studio.genlayer.com/tx/0xd911392303063cf7fd3ca24e694e269508d6e414a72aee064f0e122cad11a84e2); close [`0xb1b855…e7ee5b`](https://explorer-studio.genlayer.com/tx/0xb1b8553ed1f154344010b05b7e873c35d9609eddaad879ea72bc903745ee7ee5b) | `C-1 VALID/PASS`, `C-2 VALID/PASS`; run `PASS`, `pass=2`, historical/current certification `true` |
| Defective `R-2` | open [`0x69835d…462ada`](https://explorer-studio.genlayer.com/tx/0x69835dd5557332ee5b71cb58b4aaefe7f83c46a35d0729de6e6a68b7e14462ada); captures [`C-3`](https://explorer-studio.genlayer.com/tx/0x63b5654514cf794ccd67bef5681dae468031605a50a34baa318815c81eeecc022), [`C-4`](https://explorer-studio.genlayer.com/tx/0x7adebcc3cc1d8bf947826d6ff33bcfe31cd3159197dcbdc39bc58227fb227b262); evaluates [`C-3`](https://explorer-studio.genlayer.com/tx/0xdbc97c85e2552de200efe01308af587529c876b708b2f860acb0b7b8f00017ad5), [`C-4`](https://explorer-studio.genlayer.com/tx/0x974afe1b6d26db716fe66c1ed82a46ff5889d5e3fd77e984510c8f628aee8e810); close [`0x7695f6…1c045e`](https://explorer-studio.genlayer.com/tx/0x7695f6cd69c126a19646f287d8dc1710b44babc28753438921a589f07e11c045e) | `C-3 VALID/FAIL`, `C-4 VALID/PASS`; run `FAIL`, `fail=1`, certification `false` |
| Invalid transformation `R-4` | open [`0xb8a6dd…56b2fe`](https://explorer-studio.genlayer.com/tx/0xb8a6ddc6fe8a08cad5d0d506e7e7d3c946db9dc6298e182eb64f2034a1556b2fe); captures [`C-5`](https://explorer-studio.genlayer.com/tx/0x5e0dfdc567fc706533763ba894850241bb93e46196c44d4a9d25c9ea3455e6a3c), [`C-6`](https://explorer-studio.genlayer.com/tx/0x0a5afb38a531f427468ac67295d3b16ded37d86cc1540a48bc0df6aaecdd1db93); evaluates [`C-5`](https://explorer-studio.genlayer.com/tx/0xe7ec0f4b1f65e3dbc97eb32c93421e680996908cc1e097830ca696af007bcbf2), [`C-6`](https://explorer-studio.genlayer.com/tx/0x10d716a2fabdb2783a3578c7251d5fc0b0f39a144a9016b46604b3a4ea01d0d); close [`0x57142e…e41bb2`](https://explorer-studio.genlayer.com/tx/0x57142e60ab55e0e363d7fd136740765cbabcd62829ce1f0578bf09d612ee41bb2) | `C-5/C-6 INVALID/MATERIAL_DIFFERENCE → INCONCLUSIVE`; run `INCONCLUSIVE`, `inconclusive=2`, certification `false` |

The exact stable run readback is `state=CLOSED, outcome=PASS, pass=2, fail=0, inconclusive=0`. The defective readback is `state=CLOSED, outcome=FAIL, pass=1, fail=1, inconclusive=0`. The invalid readback is `state=CLOSED, outcome=INCONCLUSIVE, pass=0, fail=0, inconclusive=2`.

## Recheck and consumer proofs

| Proof | Transaction / readback |
| --- | --- |
| Same tester recheck rejected | [`0x0c7421…55f5f9`](https://explorer-studio.genlayer.com/tx/0x0c7421a85a5a529a31a4560dfdba4792e104621404a15a095eee9db60a555f5f9), finalized with leader and validators `ERROR` |
| Independent recheck `R-3` | open [`0x10c612…732b67`](https://explorer-studio.genlayer.com/tx/0x10c61221ebe481143694bff539943f694125634fb36d5ff4bec311a58b7732b67), captures [`C-1`](https://explorer-studio.genlayer.com/tx/0x3a579c9a4110489a5fd81ea134faf69a31b9c070bb7299b3cf54488a0b77125aa), [`C-2`](https://explorer-studio.genlayer.com/tx/0xe6f421561c7708e535b2d0be12a3d6ff1e098c52ab3790d63a8127ea8b4465a1f), evaluates [`C-1`](https://explorer-studio.genlayer.com/tx/0x472c2d640ff3ebf018ddc8fd8339907e3ed87a335fd7d5cf3da1237a64bb96121), [`C-2`](https://explorer-studio.genlayer.com/tx/0x88c29ffa004548f0eb7a38340494c67b838d3f2c002e6dbf779eb945c466c74c2), close [`0xe6a3ee…d7e3ef`](https://explorer-studio.genlayer.com/tx/0xe6a3ee063f698ed8ea497b8cd4def1793abdb0ba59504621a5c9ea3695dd7e3ef) | `R-3 PASS`; parent `R-1` readback unchanged |
| Unknown run rejected by primary consumer | [`0xd7ddaa…4b2634`](https://explorer-studio.genlayer.com/tx/0xd7ddaaafaca7b76d14fbfcc76f91abd3e64689434a456690935ab31ae044b2634), finalized execution `ERROR`; status stayed inactive |
| Exact stable PASS activates primary consumer | [`0x91a57d…bedbc7`](https://explorer-studio.genlayer.com/tx/0x91a57da2bddb10805bbbd6e09766d34238414c563a63485589735e98f8bbedbc7), finalized execution `SUCCESS`; status `activated=true, run_id=R-1` |
| Replay rejected | [`0xd1ce87…df0813`](https://explorer-studio.genlayer.com/tx/0xd1ce8714700da87fdf2706fc329dffebfcb2a32778448015b0281cbdf2ddf0813), finalized execution `ERROR`; primary status unchanged |
| Correctly bound FAIL consumer rejects `R-2` | [`0xbd51e6…48a685`](https://explorer-studio.genlayer.com/tx/0xbd51e67280066331754548ae9edbba5cd4d4cc0b56c8b241afe307d64b448a685), finalized execution `ERROR`; negative consumer status stayed inactive |

## Consensus diagnosis

See [`CONSENSUS.md`](CONSENSUS.md). The old `MAJORITY_DISAGREE` was observed on the superseded registry, but the exact validator reasoning was not available from the required RPC. The debug methods tested returned `Method not found`. The exact-path equality failure was reproduced in controlled Direct Mode, so the correction is evidence-backed as a liveness fix without claiming unavailable validator reasoning. The final live equivalent evaluation finalized `MAJORITY_AGREE` and stored `VALID / RELATION_SATISFIED / PASS`.

## CI and release state

The final release commit and its completed workflow are recorded here. The earlier failed run `42853149930` was caused by the cross-platform raw line-ending hash check and is superseded by the corrected source gate.

| Item | Result |
| --- | --- |
| Final GitHub Actions run | [42853778681 — success](https://github.com/ometere123/metamorph/actions/runs/42853778681) |
| Contract source commit | `5f6d2e0`; deployed bytes and the final contract implementation are source-matched to this commit |
| CI-verified release predecessor | [`a578ba332a159e6b08c833d7094a258ec0c4bc35`](https://github.com/ometere123/metamorph/commit/a578ba332a159e6b08c833d7094a258ec0c4bc35); the final evidence-only closeout commit is reported separately |
| Submission scope | Contract-only; no frontend, backend, database, Docker or application wallet integration |
