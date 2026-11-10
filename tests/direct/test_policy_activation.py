"""Reference policy activation and adversarial semantic-boundary tests.

These tests use the pinned GenVM v0.2.12 Direct Mode runner.  Cross-contract
views are stubbed at the VM boundary here; finalized multi-contract behaviour
is recorded separately in the StudioNet evidence ledger.
"""
import json
import sys
from pathlib import Path

import pytest
from gltest.direct import VMContext, create_address, deploy_contract


ROOT = Path(__file__).resolve().parents[2]
TARGET = ROOT / "contracts" / "policy_target.py"
ACTIVATION = ROOT / "contracts" / "policy_activation.py"


def payload(**overrides):
    value = {
        "applicant_id": "applicant-1",
        "received_day": "THU",
        "verified": True,
        "signed_receipt": True,
        "experience_years": 4,
        "tone": "neutral",
    }
    value.update(overrides)
    return json.dumps(value)


class Adapter:
    def __init__(self, target):
        self.target = target

    def view(self):
        return self.target


def address_string(value):
    if isinstance(value, bytes):
        return "0x" + value.hex()
    return str(value).lower()


def test_reference_policy_checks_real_prerequisites_and_exposes_defect():
    stable_vm = VMContext()
    with stable_vm.activate():
        stable = deploy_contract(TARGET, stable_vm, False, sdk_version="v0.2.12")
        allowed = json.loads(stable.evaluate_metamorph(payload()))
        tone_changed = json.loads(stable.evaluate_metamorph(payload(tone="urgent")))
        missing_receipt = json.loads(stable.evaluate_metamorph(payload(signed_receipt=False)))
        more_experience = json.loads(stable.evaluate_metamorph(payload(experience_years=6)))
        mixed_direction = json.loads(stable.evaluate_metamorph(
            payload(experience_years=6, verified=False)))

        assert allowed == {"decision": "ALLOW", "score_bps": 6000}
        assert tone_changed == allowed
        assert missing_receipt["decision"] == "DENY"
        assert more_experience["decision"] == "ALLOW"
        assert more_experience["score_bps"] > allowed["score_bps"]
        assert mixed_direction["decision"] == "DENY"

        with stable_vm.expect_revert("Unexpected policy payload fields"):
            stable.evaluate_metamorph(payload(extra="untrusted"))
        with stable_vm.expect_revert("verified must be boolean"):
            stable.evaluate_metamorph(payload(verified=1))

    defective_vm = VMContext()
    with defective_vm.activate():
        defective = deploy_contract(TARGET, defective_vm, True, sdk_version="v0.2.12")
        cosmetic_bug = json.loads(defective.evaluate_metamorph(payload(tone="urgent")))
        assert cosmetic_bug == {"decision": "DENY", "score_bps": 0}


def test_policy_activation_requires_exact_certification_and_authorized_actor(monkeypatch):
    target_vm = VMContext()
    with target_vm.activate():
        reference_target = deploy_contract(TARGET, target_vm, False, sdk_version="v0.2.12")
        manifest = json.loads(reference_target.get_policy_manifest())

    vm = VMContext()
    with vm.activate():
        registry_addr = create_address("policy-registry")
        candidate_addr = create_address("policy-candidate")
        authorized = create_address("policy-activator")
        unauthorized = create_address("policy-unauthorized")
        requester = create_address("policy-requester")
        target_record = json.dumps({
            "id": "T-1", "address": address_string(candidate_addr),
            "label": "Reference eligibility policy", "version": manifest["version"],
            "registrant": address_string(create_address("registrant")),
        })

        class RegistryView:
            def is_certified_current(self, run_id, suite_id, target_id, expected_hash):
                return (run_id, suite_id, target_id, expected_hash) == (
                    "R-1", "S-1", "T-1", "a" * 64)

            def get_target(self, target_id):
                assert target_id == "T-1"
                return target_record

        class TargetView:
            def get_policy_manifest(self):
                return json.dumps({"schema": "metamorph.policy/1", **manifest}, sort_keys=True)

            def evaluate_policy(self, raw):
                obj = json.loads(raw)
                return json.dumps({"decision": "ALLOW" if obj["signed_receipt"] else "DENY",
                                   "score_bps": 6000 if obj["signed_receipt"] else 0})

        activation = deploy_contract(ACTIVATION, vm, registry_addr, "T-1", "S-1",
                                     "a" * 64, "R-1", candidate_addr,
                                     manifest["policy_id"], manifest["version"],
                                     manifest["policy_digest"], authorized,
                                     sdk_version="v0.2.12")
        module = sys.modules[activation.__class__.__module__]
        registry_adapter = Adapter(RegistryView())
        candidate_adapter = Adapter(TargetView())
        monkeypatch.setattr(module.gl, "get_contract_at", lambda address: {
            address_string(registry_addr): registry_adapter,
            address_string(candidate_addr): candidate_adapter,
        }[address_string(address)])

        with vm.prank(unauthorized), vm.expect_revert("Unauthorized activator"):
            activation.activate("R-1")
        with vm.prank(authorized):
            activation.activate("R-1")
        assert activation.status() == {
            "activated": True, "run_id": "R-1", "target_id": "T-1",
            "suite_id": "S-1", "authorization_count": 0,
        }
        assert activation.is_authorized(payload()) is True
        assert activation.is_authorized(payload(signed_receipt=False)) is False

        with vm.prank(requester):
            assert activation.authorize("request-1", payload()) == "AUTHORIZED"
        assert json.loads(activation.get_authorization("request-1"))["decision"] == "ALLOW"
        assert activation.status()["authorization_count"] == 1
        with vm.prank(requester), vm.expect_revert("Authorization already recorded"):
            activation.authorize("request-1", payload())
        with vm.prank(requester), vm.expect_revert("Policy denied authorization"):
            activation.authorize("request-2", payload(signed_receipt=False))
        assert activation.status()["authorization_count"] == 1


def test_policy_activation_rejects_noncertified_run_without_mutation(monkeypatch):
    vm = VMContext()
    with vm.activate():
        registry_addr = create_address("unqualified-registry")
        candidate_addr = create_address("unqualified-candidate")
        authorized = create_address("unqualified-activator")
        manifest = {
            "policy_id": "eligibility-policy-v1",
            "version": "eligibility-policy-v1",
            "policy_digest": "b" * 64,
        }

        class RegistryView:
            def is_certified_current(self, *_):
                return False

            def get_target(self, *_):
                raise AssertionError("target must not be read after certification rejection")

        class CandidateView:
            def get_policy_manifest(self):
                return json.dumps({"schema": "metamorph.policy/1", **manifest})

        class AdapterView:
            def __init__(self, value):
                self.value = value

            def view(self):
                return self.value

        activation = deploy_contract(ACTIVATION, vm, registry_addr, "T-9", "S-9", "c" * 64,
                                     "R-9", candidate_addr, manifest["policy_id"],
                                     manifest["version"], manifest["policy_digest"], authorized,
                                     sdk_version="v0.2.12")
        module = sys.modules[activation.__class__.__module__]
        monkeypatch.setattr(module.gl, "get_contract_at", lambda address: AdapterView(
            RegistryView() if address_string(address) == address_string(registry_addr)
            else CandidateView()))
        with vm.prank(authorized), vm.expect_revert("No exact-bound current Metamorph PASS"):
            activation.activate("R-9")
        assert activation.status()["activated"] is False
