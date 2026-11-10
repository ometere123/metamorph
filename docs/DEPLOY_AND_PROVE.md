# StudioNet 61999 deployment and proof record

This is the reproducible deployment record for Metamorph. The required target is always `studionet`, chain `61999` (`0xf22f`), RPC `https://studio.genlayer.com/api`, using the repository-local `genlayer@0.39.1`. Do not substitute `studio-dev`, `studio-next`, chain `61997` or the global CLI.

## 1. Reproducible preflight

```powershell
npm ci --ignore-scripts --no-audit --no-fund
python -m pip install -r requirements-dev.txt
npm exec -- genlayer network set studionet
npm run check:network
npm run check:live-network
npm exec -- genlayer --version
npm exec -- genlayer network info
```

`check:network` verifies the repository-local CLI, selected alias and configuration. `check:live-network` sends JSON-RPC `eth_chainId` to the exact required endpoint and requires `0xf22f` / `61999`. A configuration file or alias alone is not sufficient.

The final preflight returned:

```text
PASS: studionet / chain 61999 / local GenLayer CLI 0.39.1
PASS: live https://studio.genlayer.com/api eth_chainId=0xf22f (61999)
```

## 2. Local quality gates

```powershell
python -m compileall -q contracts tests
python -m pytest tests/offline -q
python -m pytest tests/direct -q
python -m pytest tests -q
$env:GENVM_VERSION = 'v0.2.12'
python -m genvm_linter.cli check contracts/metamorph.py --json
python -m genvm_linter.cli check contracts/fixture_target.py --json
python -m genvm_linter.cli check contracts/fixture_consumer.py --json
python -m genvm_linter.cli schema contracts/metamorph.py --json
python -m genvm_linter.cli schema contracts/fixture_target.py --json
python -m genvm_linter.cli schema contracts/fixture_consumer.py --json
```

The final result was 36 offline tests, 15 Direct Mode tests and 51 total tests passed. Linter `0.11.0` accepted all three contracts and all three schema commands succeeded. Direct Mode uses controlled VM-boundary mocks; the multi-contract proof is the live StudioNet evidence below.

## 3. Final deployments

All deployment receipts were polled to `FINALIZED` and checked for successful GenVM execution, not merely accepted submission.

| Artifact | Address | Deployment transaction | Receipt |
| --- | --- | --- | --- |
| Stable fixture (`inconsistent=False`) | [`0xE763C5294ea266D2C17106fFd6d5136A6d607C22`](https://explorer-studio.genlayer.com/address/0xE763C5294ea266D2C17106fFd6d5136A6d607C22) | [`0x76f717481f6eb37e6d5105dd81770121840e1a72be31752faafa8d4ad1cb7d49`](https://explorer-studio.genlayer.com/tx/0x76f717481f6eb37e6d5105dd81770121840e1a72be31752faafa8d4ad1cb7d49) | `FINALIZED`, `MAJORITY_AGREE`, `SUCCESS` |
| Defective fixture (`inconsistent=True`) | [`0x286345CcD4A86560e8F97D1Fe2bc140724cfA354`](https://explorer-studio.genlayer.com/address/0x286345CcD4A86560e8F97D1Fe2bc140724cfA354) | [`0xe6492eab68d8878fd3769554af18263b68fdab215c5391f810c71d140ca34a92`](https://explorer-studio.genlayer.com/tx/0xe6492eab68d8878fd3769554af18263b68fdab215c5391f810c71d140ca34a92) | `FINALIZED`, `MAJORITY_AGREE`, `SUCCESS` |
| **Metamorph registry** | [`0x4a7F6a372d3A686302d1c4f5f162386Ab85aFA8b`](https://explorer-studio.genlayer.com/address/0x4a7F6a372d3A686302d1c4f5f162386Ab85aFA8b) | [`0x02aebfe82ccbf12c9ec2956cc1f331a1daa72afb4553731a0bf78e2342868ce8`](https://explorer-studio.genlayer.com/tx/0x02aebfe82ccbf12c9ec2956cc1f331a1daa72afb4553731a0bf78e2342868ce8) | `FINALIZED`, `MAJORITY_AGREE`, `SUCCESS` |
| Stable-PASS consumer | [`0x94312d8de2282485A939953E93De097FD2acf12e`](https://explorer-studio.genlayer.com/address/0x94312d8de2282485A939953E93De097FD2acf12e) | [`0x293a8d51cd2e7091066afbebe939a7c7bf77419002479347080032adae1d4fa0`](https://explorer-studio.genlayer.com/tx/0x293a8d51cd2e7091066afbebe939a7c7bf77419002479347080032adae1d4fa0) | `FINALIZED`, `MAJORITY_AGREE`, `SUCCESS` |
| FAIL-gate consumer | [`0x3EFCF9fb9Ce7946db998DA2ee28E026b85Cc440b`](https://explorer-studio.genlayer.com/address/0x3EFCF9fb9Ce7946db998DA2ee28E026b85Cc440b) | [`0xc5b0c9770f725b32ee0973ab6d8df0a749aa3627c18350c33a9769276df5daed`](https://explorer-studio.genlayer.com/tx/0xc5b0c9770f725b32ee0973ab6d8df0a749aa3627c18350c33a9769276df5daed) | `FINALIZED`, `MAJORITY_AGREE`, `SUCCESS` |

The registry constructor has no arguments. The consumer constructor was encoded with a typed `CalldataAddress`, the final registry address, and the exact stable or defective suite binding. No plain text address was used for the ABI address parameter.

## 4. Live lifecycle summary

The final registry recorded stable target `T-1` and defective target `T-2`, then froze:

- `S-1` → `T-1`, cases `C-1` equivalent tone change and `C-2` strengthened experience change, digest `299da4c043615d7ef372903d7ff979577e69182e0fbda648a6ac075ee02a6848`.
- `S-2` → `T-2`, comparable cases `C-3` and `C-4`, digest `88c0efd006eefe4cf14ccfe956b3d8227a86e9a7fd6893b028085260c9556bb7`.
- `S-3` → `T-1`, two intentionally invalid equivalent claims, digest `a3a39b78bb17eb020bb7e378b0688cd4684eae4b93b4081e618c8f26616b9e3d`.

The authoritative transaction-by-transaction table is in [`REVIEWER_EVIDENCE.md`](REVIEWER_EVIDENCE.md).

Observed finalized outcomes:

| Run | Readback | Certification |
| --- | --- | --- |
| `R-1` stable | `CLOSED`, `PASS`, `pass=2`, `fail=0`, `inconclusive=0` | historical `true`, current `true` |
| `R-2` defective | `CLOSED`, `FAIL`, `pass=1`, `fail=1`, `inconclusive=0` | historical `false`, current `false` |
| `R-4` invalid transformation | `CLOSED`, `INCONCLUSIVE`, `pass=0`, `fail=0`, `inconclusive=2` | historical `false`, current `false` |
| `R-3` independent recheck | `CLOSED`, `PASS`, `pass=2`, parent `R-1` | historical `true`, current `true`; `R-1` unchanged |

The stable fixture's public manifest was `fixture-v1-stable` and it returned `ALLOW / 6000` for both neutral and urgent tone. The defective fixture's manifest was `fixture-v1-broken` and it returned `ALLOW / 6000` for neutral but `DENY / 0` for urgent.

## 5. Consumer proof

The primary consumer is bound to registry `0x4a7F…FA8b`, suite `S-1`, target `T-1`, and the exact stable digest. Its current certification call is a genuine typed cross-contract public view.

1. `R-999` finalized with execution `ERROR`; status remained inactive.
2. `R-1` finalized with execution `SUCCESS`; status became `activated=true, run_id=R-1`.
3. Reusing `R-1` finalized with execution `ERROR`; status remained unchanged.

A separately deployed consumer bound to `S-2/T-2` and the exact defective digest rejected `R-2` with finalized execution `ERROR`, proving FAIL-gating separately from an identity mismatch.

## 6. Source verification

`genlayer-js getContractCode` returned exact byte-for-byte equality with the local committed source for the final registry, both fixture deployments and both consumers. SHA-256 values are in [`SOURCE_SHA256_MANIFEST.json`](../SOURCE_SHA256_MANIFEST.json). The source commit containing the final contract implementation is `5f6d2e0`; the release commit also contains the evidence and documentation but does not alter those contract bytes.

## 7. Operational cautions

- The earlier registry deployment at `0x746ea06755af60d06DEe75993c9dE75fD6336cE9` is superseded and is not a current release address.
- A finalized receipt with execution `ERROR` is a finalized rejection, not a successful state transition.
- Target version is target-declared metadata, not cryptographic bytecode identity; current certification is therefore version-based. The source parity proof applies to the deployments recorded above.
- Direct Mode and live StudioNet evidence are separate categories.
