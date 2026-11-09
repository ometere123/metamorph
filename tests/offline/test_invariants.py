import json
import sys
from pathlib import Path

import pytest
from gltest.direct import VMContext, load_contract_class


CONTRACT = Path(__file__).resolve().parents[2] / "contracts" / "metamorph.py"


@pytest.fixture(scope="module")
def module():
    vm = VMContext()
    with vm.activate():
        cls = load_contract_class(CONTRACT, vm, sdk_version="v0.2.12")
        yield sys.modules[cls.__module__]


@pytest.mark.parametrize(
    "relation,a,b,tolerance,expected",
    [
        ("EQUIVALENT", ("ALLOW", 7000), ("ALLOW", 7000), 0, True),
        ("EQUIVALENT", ("ALLOW", 7000), ("ALLOW", 6900), 50, False),
        ("EQUIVALENT", ("ALLOW", 7000), ("ALLOW", 6950), 50, True),
        ("EQUIVALENT", ("ALLOW", 7000), ("DENY", 7000), 0, False),
        ("STRENGTHENED", ("REVIEW", 3000), ("ALLOW", 5000), 0, True),
        ("STRENGTHENED", ("ALLOW", 7000), ("REVIEW", 8000), 0, False),
        ("STRENGTHENED", ("ALLOW", 7000), ("ALLOW", 6900), 0, False),
        ("WEAKENED", ("ALLOW", 7000), ("REVIEW", 5000), 0, True),
        ("WEAKENED", ("REVIEW", 3000), ("ALLOW", 2000), 0, False),
        ("WEAKENED", ("DENY", 3000), ("DENY", 3100), 0, False),
    ],
)
def test_deterministic_metamorphic_comparator(module, relation, a, b, tolerance, expected):
    left = {"decision": a[0], "score_bps": a[1]}
    right = {"decision": b[0], "score_bps": b[1]}
    assert module.compare_target_outcomes(relation, left, right, tolerance) is expected


def test_canonical_hash_ignores_dict_order(module):
    assert module.digest({"a": 1, "b": 2}) == module.digest({"b": 2, "a": 1})


@pytest.mark.parametrize("raw", [
    {"relation": "VALID", "reason_code": "RELATION_SATISFIED", "evidence_paths": ["original.years", "variant.years"]},
    {"relation": "INVALID", "reason_code": "MATERIAL_DIFFERENCE", "evidence_paths": ["variant.years", "original.years"]},
    {"relation": "AMBIGUOUS", "reason_code": "INSUFFICIENT_BASIS", "evidence_paths": ["original.years", "variant.years"]},
])
def test_semantic_decision_valid_shapes(module, raw):
    outcome = module.clean_semantic_result(raw, {"years": 5}, {"years": 6})
    assert outcome["evidence_paths"] == ["original.years", "variant.years"]


@pytest.mark.parametrize("broken", [
    {"relation": "VALID", "reason_code": "MATERIAL_DIFFERENCE", "evidence_paths": ["original.years", "variant.years"]},
    {"relation": "INVALID", "reason_code": "RELATION_SATISFIED", "evidence_paths": ["original.years", "variant.years"]},
    {"relation": "PASS", "reason_code": "RELATION_SATISFIED", "evidence_paths": ["original.years", "variant.years"]},
    {"relation": "VALID", "reason_code": "RELATION_SATISFIED", "evidence_paths": ["original.years", "original.years"]},
    {"relation": "VALID", "reason_code": "RELATION_SATISFIED", "evidence_paths": ["original.years", "variant.missing"]},
    {"relation": "VALID", "reason_code": "RELATION_SATISFIED", "evidence_paths": ["original.years", "original.extra"]},
    {"relation": "VALID", "reason_code": "RELATION_SATISFIED", "evidence_paths": []},
    {"relation": "VALID", "reason_code": "RELATION_SATISFIED", "evidence_paths": ["original.years", "variant.years"], "injected": 1},
])
def test_rejects_untrustworthy_model_output(module, broken):
    with pytest.raises(Exception):
        module.clean_semantic_result(broken, {"years": 5}, {"years": 6})


@pytest.mark.parametrize("body", [
    "not json", "[]", "{}", '{"a":1,"a":2}',
])
def test_rejects_malformed_input_or_empty_object(module, body):
    with pytest.raises(Exception):
        module.object_json(body, "test", 100)


def test_target_output_is_strict_and_bounded(module):
    assert module.target_result('{"decision":"ALLOW","score_bps":9000}') == {"decision":"ALLOW","score_bps":9000}
    for bad in ['{"decision":"ALLOW","score_bps":true}', '{"decision":"PASS","score_bps":1}',
                '{"decision":"ALLOW","score_bps":10001}', '{"decision":"ALLOW","score_bps":0,"extra":1}']:
        with pytest.raises(Exception):
            module.target_result(bad)


def test_prompts_never_include_target_outputs(module):
    case = {"relation":"EQUIVALENT", "note":"tone only", "original":{"tone":"a"}, "variant":{"tone":"b"}}
    snapshot = {"digest":"a" * 64, "original_output":{"decision":"ALLOW","score_bps":9000}}
    prompt = module.semantic_prompt("tone does not matter", case, snapshot)
    assert 'original_output' not in prompt
    assert '9000' not in prompt
    assert 'untrusted data' in prompt


def test_repository_network_is_exactly_61999():
    root = CONTRACT.parents[1]
    network = json.loads((root / "network.json").read_text())
    package = json.loads((root / "package.json").read_text())
    assert network == {"network":"studionet", "chainId":61999, "rpc":"https://studio.genlayer.com/api", "explorer":"https://genlayer-explorer.vercel.app"}
    assert package["devDependencies"]["genlayer"] == "0.39.1"
