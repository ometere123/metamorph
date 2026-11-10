"""Direct Mode scenarios. This is NOT a substitute for live StudioNet proof."""
import json
import sys
from pathlib import Path

import pytest
from gltest.direct import VMContext, create_address, deploy_contract


ROOT = Path(__file__).resolve().parents[2]
MAIN = ROOT / "contracts" / "metamorph.py"
TARGET = ROOT / "contracts" / "fixture_target.py"
CONSUMER = ROOT / "contracts" / "fixture_consumer.py"

STABLE = {"relation": "VALID", "reason_code": "RELATION_SATISFIED",
          "evidence_paths": ["original.experience_years", "variant.experience_years"]}
INCONCLUSIVE = {"relation": "AMBIGUOUS", "reason_code": "INSUFFICIENT_BASIS",
                "evidence_paths": ["original.experience_years", "variant.experience_years"]}
INVALID = {"relation": "INVALID", "reason_code": "MATERIAL_DIFFERENCE",
           "evidence_paths": ["original.experience_years", "variant.experience_years"]}


class Adapter:
    def __init__(self, target):
        self.target = target

    def view(self):
        return self.target


class FakeTarget:
    # gltest Direct Mode runs one contract class per VM. Cross-contract target
    # views are deliberately stubbed here; the real adapter is a separate IC.
    def __init__(self, inconsistent=False):
        self.inconsistent = inconsistent
        self.version_override = ""

    def get_metamorph_manifest(self):
        return json.dumps({"schema":"metamorph.adapter/1",
                           "version":self.version_override or (
                               "fixture-v1-broken" if self.inconsistent else "fixture-v1-stable")})

    def evaluate_metamorph(self, payload):
        obj = json.loads(payload)
        score = 2000 + obj["experience_years"] * 500 + (2000 if obj["verified"] else 0)
        if self.inconsistent and obj.get("tone") == "urgent":
            score = 0
        decision = "ALLOW" if score >= 5000 else ("REVIEW" if score >= 3000 else "DENY")
        return json.dumps({"decision":decision, "score_bps":score})


@pytest.fixture
def lab(monkeypatch):
    vm = VMContext()
    with vm.activate():
        # genvm-v0.2.12 is compatible with stable 61999 and local CLI 0.39.1.
        registry = deploy_contract(MAIN, vm, sdk_version="v0.2.12")
        stable_target = FakeTarget(False)
        broken_target = FakeTarget(True)
        addresses = [create_address(name) for name in ("registrant", "curator", "author", "tester", "tester-2")]
        taddrs = [create_address("stable-target"), create_address("broken-target")]
        targets = {str(taddrs[0]).lower(): Adapter(stable_target), str(taddrs[1]).lower(): Adapter(broken_target)}
        module = sys.modules[registry.__class__.__module__]
        monkeypatch.setattr(module.gl, "get_contract_at", lambda a: targets[str(a).lower()])
        yield vm, registry, taddrs, addresses, module, targets


def setup_suite(lab, broken=False):
    vm, registry, taddrs, actors, module, targets = lab
    registrant, curator, author, tester, _ = actors
    with vm.prank(registrant):
        target_id = registry.register_target(taddrs[1 if broken else 0], "Fixture")
    with vm.prank(curator):
        suite_id = registry.create_suite(target_id, "Tone and experience invariants",
            "Eligibility depends only on verified status and experience_years; tone is cosmetic; "
            "more experience with verification fixed is favorable, less experience is unfavorable.", author)
    originals = [
        ("EQUIVALENT", {"verified":True, "experience_years":4, "tone":"neutral"},
         {"verified":True, "experience_years":4, "tone":"urgent"}),
        ("STRENGTHENED", {"verified":True, "experience_years":2, "tone":"neutral"},
         {"verified":True, "experience_years":4, "tone":"neutral"}),
        ("WEAKENED", {"verified":True, "experience_years":4, "tone":"neutral"},
         {"verified":True, "experience_years":2, "tone":"neutral"}),
    ]
    cases = []
    with vm.prank(author):
        for relation, left, right in originals:
            cases.append(registry.add_case(suite_id, relation, json.dumps(left), json.dumps(right),
                                           "Frozen inputs differ only in stated transformation"))
    with vm.prank(curator):
        suite_digest = registry.freeze_suite(suite_id)
    with vm.prank(tester):
        run_id = registry.open_run(suite_id)
    return suite_id, target_id, suite_digest, run_id, cases


def run_cases(lab, run_id, case_ids, answer=STABLE):
    vm, registry, _, actors, _, _ = lab
    with vm.prank(actors[3]):
        vm.mock_llm("You are independently evaluating", json.dumps(answer))
        for case_id in case_ids:
            registry.capture_case(run_id, case_id)
            registry.evaluate_case(run_id, case_id)
        return registry.close_run(run_id)


def test_stable_target_gets_exact_pass(lab):
    vm, registry, _, actors, _, _ = lab
    sid, tid, h, rid, ids = setup_suite(lab)
    assert run_cases(lab, rid, ids) == "PASS"
    assert registry.is_certified(rid, sid, tid, h) is True
    assert registry.is_certified_current(rid, sid, tid, h) is True
    assert registry.is_certified(rid, sid, tid, "f" * 64) is False
    assert json.loads(registry.get_run(rid))["pass"] == 3


def test_target_version_change_invalidates_current_gate_but_not_history(lab):
    vm, registry, taddrs, _, _, targets = lab
    sid, tid, h, rid, ids = setup_suite(lab)
    assert run_cases(lab, rid, ids) == "PASS"
    targets[str(taddrs[0]).lower()].target.version_override = "fixture-v2"
    assert registry.is_certified(rid, sid, tid, h) is True
    assert registry.is_certified_current(rid, sid, tid, h) is False


def test_cosmetic_bias_is_failure_not_invalid_test(lab):
    _, registry, _, _, _, _ = lab
    sid, tid, h, rid, ids = setup_suite(lab, broken=True)
    assert run_cases(lab, rid, ids) == "FAIL"
    assert registry.is_certified(rid, sid, tid, h) is False
    assert json.loads(registry.get_verdict(rid, ids[0]))["outcome"] == "FAIL"


@pytest.mark.parametrize("answer", [INCONCLUSIVE, INVALID])
def test_invalid_or_uncertain_transformation_cannot_certify(lab, answer):
    _, registry, _, _, _, _ = lab
    sid, tid, h, rid, ids = setup_suite(lab)
    assert run_cases(lab, rid, ids, answer=answer) == "INCONCLUSIVE"
    assert not registry.is_certified(rid, sid, tid, h)


def test_cannot_close_incomplete_run(lab):
    vm, registry, _, actors, _, _ = lab
    _, _, _, rid, _ = setup_suite(lab)
    with vm.prank(actors[3]), vm.expect_revert("Every case needs a verdict"):
        registry.close_run(rid)


def test_suite_authorization_and_freeze(lab):
    vm, registry, _, actors, _, _ = lab
    sid, _, _, rid, _ = setup_suite(lab)
    with vm.prank(actors[2]), vm.expect_revert("Suite is frozen"):
        registry.add_case(sid, "EQUIVALENT", '{"a":1}', '{"a":2}', "Too late")
    with vm.prank(actors[0]), vm.expect_revert("Independent tester required"):
        registry.open_run(sid)


def test_double_capture_rejected(lab):
    vm, registry, _, actors, _, _ = lab
    _, _, _, rid, ids = setup_suite(lab)
    with vm.prank(actors[3]):
        registry.capture_case(rid, ids[0])
        with vm.expect_revert("Case already captured"):
            registry.capture_case(rid, ids[0])


def test_recheck_is_distinct_immutable_run(lab):
    vm, registry, _, actors, _, _ = lab
    sid, _, _, rid, ids = setup_suite(lab)
    assert run_cases(lab, rid, ids) == "PASS"
    with vm.prank(actors[3]), vm.expect_revert("different tester"):
        registry.open_run(sid, rid)
    with vm.prank(actors[4]):
        rid2 = registry.open_run(sid, rid)
    assert rid2 != rid
    assert json.loads(registry.get_run(rid))["state"] == "CLOSED"
    assert json.loads(registry.get_run(rid2))["state"] == "OPEN"


def test_validator_rejects_forged_leader_and_provenance(lab):
    vm, registry, _, actors, _, _ = lab
    _, _, _, rid, ids = setup_suite(lab)
    with vm.prank(actors[3]):
        vm.mock_llm("You are independently evaluating", json.dumps(STABLE))
        registry.capture_case(rid, ids[0])
        assert registry.evaluate_case(rid, ids[0]) == "PASS"
        assert vm.run_validator() is True
        assert vm.run_validator(leader_result=INVALID) is False
        forged = {**STABLE, "evidence_paths": ["original.experience_years", "variant.imaginary"]}
        assert vm.run_validator(leader_result=forged) is False
        irrelevant = {**STABLE, "evidence_paths": ["original.tone", "variant.tone"]}
        assert vm.run_validator(leader_result=irrelevant) is False
        assert vm.run_validator(leader_error=ValueError("unavailable")) is False


def test_validator_disagreement_fails(lab):
    vm, registry, _, actors, _, _ = lab
    _, _, _, rid, ids = setup_suite(lab)
    with vm.prank(actors[3]):
        vm.mock_llm("You are independently evaluating", json.dumps(STABLE))
        registry.capture_case(rid, ids[0])
        registry.evaluate_case(rid, ids[0])
        vm.clear_mocks()
        vm.mock_llm("You are independently evaluating", json.dumps(INCONCLUSIVE))
        assert vm.run_validator() is False


@pytest.mark.parametrize("inconsistent,expected", [(False, "ALLOW"), (True, "DENY")])
def test_deployed_target_fixture_exposes_cosmetic_defect(inconsistent, expected):
    vm = VMContext()
    with vm.activate():
        fixture = deploy_contract(TARGET, vm, inconsistent, sdk_version="v0.2.12")
        result = json.loads(fixture.evaluate_metamorph(json.dumps({
            "verified": True, "experience_years": 4, "tone": "urgent"
        })))
        assert result["decision"] == expected


@pytest.mark.parametrize("certified", [True, False])
def test_actual_consumer_contract_requires_exact_certification(monkeypatch, certified):
    vm = VMContext()
    with vm.activate():
        registry_addr = create_address("registry")
        consumer = deploy_contract(CONSUMER, vm, registry_addr, "S-4", "T-8", "a" * 64,
                                   sdk_version="v0.2.12")

        class RegistryView:
            def is_certified_current(self, run_id, suite_id, target_id, expected_hash):
                assert (run_id, suite_id, target_id, expected_hash) == ("R-2", "S-4", "T-8", "a" * 64)
                return certified

        module = sys.modules[consumer.__class__.__module__]
        monkeypatch.setattr(module.gl, "get_contract_at", lambda _: Adapter(RegistryView()))
        if certified:
            consumer.activate("R-2")
            assert consumer.status() == {"activated":True, "run_id":"R-2", "suite_id":"S-4", "target_id":"T-8"}
            with vm.expect_revert("Already activated"):
                consumer.activate("R-2")
        else:
            with vm.expect_revert("No exact-bound"):
                consumer.activate("R-2")
            assert consumer.status()["activated"] is False
