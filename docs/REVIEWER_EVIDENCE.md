# Verification ledger — Metamorph

As of the initial repository build, the status is deliberately conservative. The record must be updated with real transactions **after** a funded signer executes the live test sequence.

| Item | Status | Evidence |
| --- | --- | --- |
| `studionet` / chain `61999` | Verified locally | Local `genlayer@0.39.1 network info` printed 61999 / `https://studio.genlayer.com/api` |
| CLI version | Verified locally | `npm exec -- genlayer --version` = `0.39.1` |
| GenVM linter | Verified locally | 3/3 contract files accepted; contract method schemas generated |
| Pure invariant + security tests | Verified locally | 29 offline checks passed |
| Direct Mode | Verified locally | 15 actual GenVM Direct Mode scenarios passed, v0.2.12 |
| CI | **PASS — verified on a fresh GitHub runner** | [GitHub Actions run 42718594748](https://github.com/ometere123/metamorph/actions/runs/42718594748): repository CLI/network guard, GenVM lint, and 44 offline + Direct Mode tests passed |
| StudioNet production registry deployment | **NOT YET PROVEN** | No local funded CLI account available in build environment |
| StudioNet consensus lifecycle | **NOT YET PROVEN** | No tx hashes available |
| StudioNet consumer proof | **NOT YET PROVEN** | Direct Mode consumer test is not network-level proof |
| Live source parity | **NOT YET PROVEN** | Requires deployed code fetch and comparison |

## Populate after real deployment

| Proof | Contract address | Tx hash | Final execution status | View readback | Explorer URL |
| --- | --- | --- | --- | --- | --- |
| Registry deploy | Pending | Pending | Pending | Pending | Pending |
| Stable fixture deploy | Pending | Pending | Pending | Pending | Pending |
| Broken fixture deploy | Pending | Pending | Pending | Pending | Pending |
| Stable PASS | — | Pending | Pending | Pending | Pending |
| Broken FAIL | — | Pending | Pending | Pending | Pending |
| Invalid/ambiguous INCONCLUSIVE | — | Pending | Pending | Pending | Pending |
| Consumer refusal | Pending | Pending | Pending | Pending | Pending |
| Consumer activation | Pending | Pending | Pending | Pending | Pending |
| Recheck | — | Pending | Pending | Pending | Pending |

`FINALIZED` alone is insufficient: record the actual successful execution result and read the on-chain state after finality.
