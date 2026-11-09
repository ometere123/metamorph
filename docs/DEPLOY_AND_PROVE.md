# StudioNet 61999 — deployment and live proof checklist

**The exact target is `studionet` / chain ID `61999` / `https://studio.genlayer.com/api`.** This document does not authorize changing networks or reusing the global CLI.

## 0. Prerequisites and network guard

The workstation may have global `genlayer@0.40.0rc2`. Ignore it: these commands use the **repo-local `0.39.1`** binary installed by `npm ci`.

```bash
npm ci --ignore-scripts --no-audit --no-fund
python -m pip install -r requirements-dev.txt
npm exec -- genlayer network set studionet
npm run check:network
npm exec -- genlayer --version
npm exec -- genlayer network info
```

**Stop** unless `network info` prints alias `studionet`, chain ID `61999`, RPC `https://studio.genlayer.com/api`, and the binary prints `0.39.1`.

The project has no embedded signer. Use only a user-authorized, funded StudioNet wallet already configured in the CLI, or explicitly create and fund disposable wallets with the account owner's permission. Never commit keys, mnemonics, private `.env` files, or CLI account exports.

Four distinct wallet identities are required:

1. Registrant (registers public target)
2. Suite curator (owns and freezes a suite)
3. Case author (authors cases under the curator)
4. Tester (captures and evaluates a run)

A fifth identity is needed for a recheck. CLI `account use` may be used to switch among authorized wallet identities; document only public addresses.

## 1. Full local validation

```bash
python -m compileall -q contracts tests
python -m pytest tests -q
python -m genvm_linter.cli check contracts/metamorph.py --json
python -m genvm_linter.cli check contracts/fixture_target.py --json
python -m genvm_linter.cli check contracts/fixture_consumer.py --json
```

Direct Mode and offline unit tests do not demonstrate multi-validator StudioNet consensus. Their reported outcomes must be labeled as such.

## 2. Deploy contracts on 61999

CLI `deploy` syntax was checked against the repository-local CLI `0.39.1`:

```bash
npm exec -- genlayer deploy --contract contracts/fixture_target.py --rpc https://studio.genlayer.com/api --args false
npm exec -- genlayer deploy --contract contracts/fixture_target.py --rpc https://studio.genlayer.com/api --args true
npm exec -- genlayer deploy --contract contracts/metamorph.py --rpc https://studio.genlayer.com/api
```

Record the stable target, defective target and registry addresses, deploy tx hashes, wallet addresses, current chain ID and source hashes. Do not invent these values in documentation.

Check each tx receipt, execution result and deployed source with CLI `receipt`, `schema`, `code`, and explorer; compare deployed source bytes with the repository's exact file. Wait for finalization **and** a successful execution result before calling a deployment complete.

## 3. Live lifecycle

Using role-separated, funded StudioNet wallets:

1. Register the stable and defective target addresses separately via `register_target`.
2. Create one suite for each registered target. Name an independent author address.
3. Author at least two frozen cases per suite, preferably:
   - `EQUIVALENT`: identical verified/experience facts, changed `tone` field.
   - `STRENGTHENED`: increase `experience_years`, with verification fixed.
   - `WEAKENED`: decrease `experience_years`, with verification fixed.
4. Curator freezes both suites and records their exact digest readbacks.
5. Independent tester opens both runs, captures every case, evaluates every case, then closes the runs.
6. Verify the stable fixture's exact-bound `PASS` and the defective fixture's `FAIL` on finalised successful executions. Verify `is_certified_current` is true only for the stable suite.
7. Deploy `contracts/fixture_consumer.py` with arguments: `<registry-address> <stable-suite-id> <stable-target-id> <64-char-suite-digest>`.
8. Call `activate` using the defective run ID: expect revert/refusal. Call with the valid run ID: expect one irreversible activation. A second attempt should revert.
9. Demonstrate one invalid/ambiguous input transformation that closes `INCONCLUSIVE` and fails certification.
10. Demonstrate a recheck opened by a distinct tester; record its independent receipt without mutating the prior run.

CLI writes follow the syntax below. Substitute only verified IDs/addresses, and pass JSON arguments as properly quoted strings:

```bash
npm exec -- genlayer write <registry-address> <method> --rpc https://studio.genlayer.com/api --args <arguments...>
npm exec -- genlayer call <registry-address> <view-method> --rpc https://studio.genlayer.com/api --args <arguments...>
npm exec -- genlayer receipt <transaction-hash>
npm exec -- genlayer schema <registry-address>
npm exec -- genlayer code <registry-address>
```

Consult `npm exec -- genlayer write --help` for the CLI's argument-encoding syntax (`address`, JSON strings, integers). Do not mix target IDs between the two registries/runs.

## 4. Prove validator independence

- Demonstrate ordinary full-consensus success for a valid equivalent transformation.
- Demonstrate an invalid transformation returning `INCONCLUSIVE` rather than manufacturing a target failure.
- Preferably run a deliberately conflicting semantic transformation against multiple validators and record an independently corroborated `INVALID` or `AMBIGUOUS` outcome.
- Reproduce the leader-forgery and disagreement checks with Direct Mode `vm.run_validator` and document that they are mocked-LLM tests, not live malicious network validators.

## 5. Evidence required before submission

Fill `docs/REVIEWER_EVIDENCE.md` with immutable links and actual status readbacks:

- 61999 chain/network verification
- registry/fixture/consumer contract addresses and deployment hashes
- finalised **successful** execution results plus authoritative readbacks
- stable PASS, defective FAIL, invalid INCONCLUSIVE, consumer reject/activate, recheck
- CI workflow link and committed source SHA
- byte-for-byte source parity against deployed code, or explicit limitations

**Do not claim production deployment, explorer verification, or live consumer proof until the network genuinely confirms them.**
