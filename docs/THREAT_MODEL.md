# Metamorph threat model

## Scope and protected properties

Metamorph protects the integrity of a frozen metamorphic test definition, provenance of captured target observations, deterministic comparison, exact-bound certification and one-time downstream activation. It does not prove that a target decision is objectively correct, fair or true in the external world.

The final reference integration protects a policy-activation state transition. A candidate can activate only through an immutable binding to the real registry, target, suite, digest, run, candidate policy identity and authorized activation address. A downstream authorization request is evaluated by the activated candidate and is single-use.

## Actors and trust boundaries

- **Target registrant:** binds a public target address and adapter manifest.
- **Suite curator:** creates and freezes the suite.
- **Case author:** supplies cases before freezing.
- **Independent tester:** captures, evaluates and closes a run; rechecks require another address.
- **Target:** reports public-view outputs and its own adapter version; it may be dishonest.
- **Leader and validators:** independently classify only the input transformation under frozen policy.
- **Activation actor:** the immutable actor authorized to activate the candidate policy.
- **Downstream caller:** may request policy authorization after activation; the policy result, not caller text, controls the outcome.
- **RPC/deployment operator:** can submit transactions, but has no hidden contract administrator override.

Distinct wallet addresses establish protocol role separation, not guaranteed real-world independence. Public policies, inputs, outputs and digests are not a secret store.

## Threat matrix

| Threat | Protected property | Mitigation | Evidence | Residual risk |
| --- | --- | --- | --- | --- |
| Curator/author rewrites frozen policy or cases | Frozen suite semantics | Freeze is one-way; ordered cases and target binding are hashed | Offline/Direct freeze and post-freeze mutation tests; live frozen suites | A colluding curator and author can create a bad suite before freeze |
| Unauthorized case author or freeze caller | Role boundary | Sender checks designated author and curator | Direct authorization tests; live distinct registrant/curator/author writes | Address ownership is not social independence |
| Tester substitutes target outputs or case IDs | Snapshot provenance | Registry re-reads the registered target’s two views and binds run/case/target/version/digests/tester | Direct snapshot substitution tests; live `TARGET_PUBLIC_VIEW` readbacks | A malicious target can lie through its own public view |
| Target changes after registration | Current certification | Manifest version is checked at run opening/capture/current certification | Direct version drift and unavailable-target tests; live current readbacks | Version is target-declared, not cryptographic code identity |
| Malicious leader returns a well-formed false result | Semantic consensus | Validator independently evaluates frozen policy and inputs; relation/reason signature must agree | Direct malicious-leader/disagreement tests; live validator execution statuses | Public receipts do not expose private validator reasoning |
| Evidence-path forgery or irrelevance | Semantic provenance | Paths must be real scalar leaves, paired, unique, both-sided and include a changed scalar | Direct fabricated/irrelevant/missing-path regressions | Path validity does not by itself prove semantic correctness |
| Exact path-list mismatch causes liveness failure | Successful consensus | Do not compare independent path lists byte-for-byte; retain substantive relation/reason agreement | Reproduced Direct Mode defect and live corrected equivalent PASS | Independent models can still disagree substantively and abort/fail |
| Prompt injection in policy, note or inputs | Instruction/data separation | Untrusted data delimiters, bounded schemas, independent recomputation and target-output omission | Direct prompt-injection test; live ambiguous/invalid policies | Model errors cannot be eliminated entirely |
| Invalid or ambiguous transformation certifies target | Fail-closed outcome | Only `VALID` reaches comparator; invalid/ambiguous becomes `INCONCLUSIVE` | Live `R-3` and `R-4`, Direct Mode regression tests | Semantic classification remains probabilistic/interpretive |
| Defective target passes via comparator weakness | Deterministic result | Strict output schema and deterministic decision/score comparator; no LLM PASS/FAIL | Live `R-2` deterministic FAIL and false certification | It only evaluates declared metamorphic properties |
| Cross-run, suite, target or digest substitution | Certification binding | State checks all IDs, digests, versions and target addresses; consumer constructor binds exact values | Direct binding tests; live defective/ambiguous consumers reject | A correctly bound but poorly chosen suite can still be weak |
| Stale historical PASS unlocks action | Currentness | Consumer calls `is_certified_current`, not historical-only view | Direct stale/unavailable manifest tests; live current PASS activation | Target version remains self-declared |
| Unauthorized policy activation | Consequential state | Immutable authorized activator address; exact certification and policy manifest required | Direct test and live unauthorized activation rejection | The authorized key must be protected operationally |
| Activation replay | One-time consequence | `activated` and `used_run` are immutable after success | Direct test and live replay rejection | A new consumer instance can intentionally be deployed separately |
| Downstream authorization replay | Single-use request | `request_id` TreeMap entry is checked before mutation and recorded with caller/result | Direct test and live duplicate request rejection | Request identifiers are bounded public strings |
| Denied request mutates state | Atomicity | Policy call and decision check happen before count/map write | Direct test and live denied request rejection/readback | Stable runtime atomicity is relied upon for reverted writes |
| Deployment to preview network/global CLI | Release integrity | Repository-local CLI lock, network alias guard and live `eth_chainId` assertion | Fresh `0.39.1`, `studionet`, `0xf22f` checks | Operators must retain the locked workflow |
| Password/keystore disclosure | Deployment credential security | Helper requires interactive TTY, raw-mode masked entry, rejects non-TTY input, never accepts password in argv/env or logs | Offline source regression and manual deployment use | Terminal recording/keylogger compromise remains outside contract scope |
| Missing historical transaction indexing | Evidence integrity | Read-only verifier distinguishes missing transaction data from contradicted state; no invented receipts | Final verifier reports all configured hashes indexed; old ledgers remain labelled historical | RPC indexing can regress; explorer HTML alone is not treated as receipt proof |
| Source mismatch | Release integrity | Canonical source hashes, raw `getContractCode` hashes and address bindings in manifest | Final registry and integration addresses matched via required RPC | `getContractCode` proves retrieved source bytes, not that future code cannot change |

## Explicit non-claims

1. Metamorph does not establish real-world applicant identity, fairness, legal correctness or off-chain truth.
2. The policy target is a reference integration, not an independent third-party audit target.
3. A target-declared manifest version is not bytecode attestation.
4. Live receipts expose execution outcomes and validator vote metadata, not private validator reasoning.
5. Different domains, wallets or model providers do not automatically prove institutional independence.
6. Direct Mode’s cross-contract adapters are VM-boundary stubs; the real cross-contract proof is the separate finalized StudioNet evidence.

## Final evidence anchors

- Stable registry: [`0x5f31A604e9C3A9362A01A17c5be6b8a1440Db2dF`](https://explorer-studio.genlayer.com/address/0x5f31A604e9C3A9362A01A17c5be6b8a1440Db2dF)
- Stable PASS: `R-1`, current certification `true`.
- Defective FAIL: `R-2`, certification `false`.
- Invalid INCONCLUSIVE: `R-3`, certification `false`.
- Ambiguous INCONCLUSIVE: `R-4`, certification `false`.
- Independent recheck: `R-5`, parent `R-1`, current certification `true`.
- Source and transaction ledger: [`docs/REVIEWER_EVIDENCE.md`](REVIEWER_EVIDENCE.md).
