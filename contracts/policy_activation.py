# { "Depends": "py-genlayer:1jb45aa8ynh2a9c9xn3b7qqh8sm5q93hwfp7jqmwsfhh8jpz09h6" }
"""Metamorph-gated policy activation reference consumer.

Activation is authorized by one immutable actor and requires an exact current
Metamorph certification.  After activation, permissionless callers may submit
bounded authorization requests; the candidate policy's deterministic output
must allow the request and each request key is single-use.
"""
from genlayer import *
import json


ADAPTER_SCHEMA = "metamorph.adapter/1"
POLICY_SCHEMA = "metamorph.policy/1"
ZERO_ADDRESS = "0x" + ("0" * 40)
MAX_ID = 100
MAX_VERSION = 80
MAX_DIGEST = 64
MAX_PAYLOAD = 1500


def require(condition, message):
    if not condition:
        raise gl.vm.UserError(message)


def address_text(value):
    if isinstance(value, bytes):
        raw = "0x" + value.hex()
    elif hasattr(value, "hex"):
        encoded = str(value.hex()).lower()
        raw = encoded if encoded.startswith("0x") else "0x" + encoded
    else:
        raw = str(value).lower()
    require(raw.startswith("0x") and len(raw) == 42 and
            all(char in "0123456789abcdef" for char in raw[2:]), "Invalid address")
    require(raw != ZERO_ADDRESS, "Zero address is not allowed")
    return raw


def bounded(value, limit, label):
    require(isinstance(value, str) and 0 < len(value.strip()) <= limit,
            "Invalid " + label)
    return value.strip()


def digest_text(value):
    value = bounded(value, MAX_DIGEST, "suite digest")
    require(len(value) == MAX_DIGEST and all(char in "0123456789abcdef" for char in value.lower()),
            "Invalid suite digest")
    return value.lower()


def sender():
    return address_text(gl.message.sender_address)


def parse_object(raw, label):
    require(isinstance(raw, str) and 0 < len(raw) <= 2400, "Invalid " + label)

    def unique_pairs(pairs):
        result = {}
        for key, value in pairs:
            if key in result:
                raise ValueError("Duplicate JSON key")
            result[key] = value
        return result

    def reject_constant(token):
        raise ValueError("Non-finite JSON number")

    try:
        obj = json.loads(raw, object_pairs_hook=unique_pairs, parse_constant=reject_constant)
    except Exception:
        raise gl.vm.UserError("Malformed " + label)
    require(isinstance(obj, dict), "Invalid " + label)
    return obj


def parse_policy_manifest(raw):
    obj = parse_object(raw, "policy manifest")
    require(set(obj.keys()) == {"schema", "policy_id", "version", "policy_digest"},
            "Unexpected policy manifest fields")
    require(obj["schema"] == POLICY_SCHEMA, "Unsupported policy schema")
    return {"schema": POLICY_SCHEMA,
            "policy_id": bounded(obj["policy_id"], MAX_ID, "policy_id"),
            "version": bounded(obj["version"], MAX_VERSION, "policy version"),
            "policy_digest": digest_text(obj["policy_digest"])}


def parse_target_record(raw):
    obj = parse_object(raw, "target record")
    require(set(obj.keys()) == {"id", "address", "label", "version", "registrant"},
            "Unexpected target record fields")
    return {"id": bounded(obj["id"], MAX_ID, "target id"),
            "address": address_text(obj["address"]),
            "version": bounded(obj["version"], MAX_VERSION, "target version")}


def parse_result(raw):
    obj = parse_object(raw, "policy result")
    require(set(obj.keys()) == {"decision", "score_bps"}, "Unexpected policy result fields")
    require(obj["decision"] in {"DENY", "REVIEW", "ALLOW"}, "Invalid policy decision")
    require(type(obj["score_bps"]) is int and 0 <= obj["score_bps"] <= 10000,
            "Invalid policy score")
    return obj


class PolicyActivation(gl.Contract):
    """Exact-bound, one-time policy activation with downstream authorization."""
    registry: str
    target_id: str
    suite_id: str
    suite_digest: str
    expected_run_id: str
    candidate: str
    expected_policy_id: str
    expected_policy_version: str
    expected_policy_digest: str
    authorized_activator: str
    activated: bool
    used_run: str
    authorization_count: u64
    authorizations: TreeMap[str, str]

    def __init__(self, registry: Address, target_id: str, suite_id: str,
                 suite_digest: str, expected_run_id: str, candidate: Address,
                 expected_policy_id: str, expected_policy_version: str,
                 expected_policy_digest: str, authorized_activator: Address):
        self.registry = address_text(registry)
        self.target_id = bounded(target_id, MAX_ID, "target id")
        self.suite_id = bounded(suite_id, MAX_ID, "suite id")
        self.suite_digest = digest_text(suite_digest)
        self.expected_run_id = bounded(expected_run_id, MAX_ID, "expected run id")
        self.candidate = address_text(candidate)
        self.expected_policy_id = bounded(expected_policy_id, MAX_ID, "policy id")
        self.expected_policy_version = bounded(expected_policy_version, MAX_VERSION, "policy version")
        self.expected_policy_digest = digest_text(expected_policy_digest)
        self.authorized_activator = address_text(authorized_activator)
        self.activated = False
        self.used_run = ""
        self.authorization_count = u64(0)
        self.authorizations = TreeMap()

    def _current_policy(self):
        return parse_policy_manifest(
            gl.get_contract_at(Address(self.candidate)).view().get_policy_manifest())

    def _matches_expected_policy(self, manifest):
        return (manifest["policy_id"] == self.expected_policy_id and
                manifest["version"] == self.expected_policy_version and
                manifest["policy_digest"] == self.expected_policy_digest)

    @gl.public.write
    def activate(self, run_id: str) -> None:
        require(sender() == self.authorized_activator, "Unauthorized activator")
        require(not self.activated, "Already activated")
        require(run_id == self.expected_run_id, "Unexpected run binding")
        registry_view = gl.get_contract_at(Address(self.registry)).view()
        require(registry_view.is_certified_current(
            run_id, self.suite_id, self.target_id, self.suite_digest),
                "No exact-bound current Metamorph PASS")
        target = parse_target_record(registry_view.get_target(self.target_id))
        require(target["address"] == self.candidate and
                target["version"] == self.expected_policy_version,
                "Target binding mismatch")
        manifest = self._current_policy()
        require(self._matches_expected_policy(manifest), "Policy identity mismatch")
        self.activated = True
        self.used_run = run_id

    @gl.public.view
    def status(self) -> dict:
        return {"activated": bool(self.activated), "run_id": self.used_run,
                "target_id": self.target_id, "suite_id": self.suite_id,
                "authorization_count": int(self.authorization_count)}

    @gl.public.view
    def is_authorized(self, payload: str) -> bool:
        if not self.activated:
            return False
        try:
            if not self._matches_expected_policy(self._current_policy()):
                return False
            return parse_result(gl.get_contract_at(Address(self.candidate)).view()
                                .evaluate_policy(payload))["decision"] == "ALLOW"
        except Exception:
            return False

    @gl.public.write
    def authorize(self, request_id: str, payload: str) -> str:
        require(self.activated, "Policy is not active")
        request_id = bounded(request_id, MAX_ID, "request id")
        require(not self.authorizations.get(request_id, ""), "Authorization already recorded")
        require(self._matches_expected_policy(self._current_policy()),
                "Active policy version changed")
        result = parse_result(gl.get_contract_at(Address(self.candidate)).view()
                              .evaluate_policy(payload))
        require(result["decision"] == "ALLOW", "Policy denied authorization")
        self.authorization_count += u64(1)
        self.authorizations[request_id] = json.dumps({"request_id": request_id,
                                                       "caller": sender(),
                                                       "decision": result["decision"],
                                                       "score_bps": result["score_bps"]},
                                                      sort_keys=True)
        return "AUTHORIZED"

    @gl.public.view
    def get_authorization(self, request_id: str) -> str:
        return self.authorizations.get(request_id, "")
