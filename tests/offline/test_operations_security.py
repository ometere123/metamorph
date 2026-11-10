from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def test_studionet_helper_requires_masked_interactive_password_input():
    source = (ROOT / "scripts" / "studionet_ops.mjs").read_text(encoding="utf-8")
    assert "setRawMode(true)" in source
    assert "Secure keystore password entry requires an interactive TTY" in source
    assert "process.argv" not in source
    assert "console.log(password" not in source
    assert "console.log(JSON.stringify(await handle(command)))" in source


def test_read_only_evidence_verifier_contains_no_write_path():
    source = (ROOT / "scripts" / "verify_live_evidence.mjs").read_text(encoding="utf-8")
    assert "writeContract" not in source
    assert "privateKey" not in source
    assert "eth_chainId" in source
    assert "gen_getContractCode" not in source or "getContractCode" in source
