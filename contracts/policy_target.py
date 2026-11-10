# { "Depends": "py-genlayer:1jb45aa8ynh2a9c9xn3b7qqh8sm5q93hwfp7jqmwsfhh8jpz09h6" }
"""Reference eligibility-policy target for the Metamorph integration.

This is a deliberately small, stateful-policy reference implementation rather
than a third-party contract.  It exposes the bounded Metamorph adapter and a
separate policy view consumed after activation.  The defective constructor
variant intentionally makes the cosmetic ``tone`` field decision-relevant so
that a semantically valid equivalent case produces a deterministic FAIL.
"""
from genlayer import *
import hashlib
import json


ADAPTER_SCHEMA = "metamorph.adapter/1"
POLICY_SCHEMA = "metamorph.policy/1"
POLICY_ID = "eligibility-policy-v1"
MAX_PAYLOAD = 1500
MAX_APPLICANT = 80
MAX_TONE = 40
MAX_VERSION = 80
WEEKDAYS = {"MON", "TUE", "WED", "THU", "FRI"}
INPUT_FIELDS = {"applicant_id", "received_day", "verified", "signed_receipt",
                "experience_years", "tone"}


def require(condition, message):
    if not condition:
        raise gl.vm.UserError(message)


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True)


def bounded(value, limit, label):
    require(isinstance(value, str) and 0 < len(value.strip()) <= limit,
            "Invalid " + label)
    require(not any(ord(char) < 32 and char not in "\n\t" for char in value),
            "Control bytes in " + label)
    return value.strip()


def parse_payload(raw):
    require(isinstance(raw, str) and 0 < len(raw) <= MAX_PAYLOAD,
            "Invalid policy payload length")

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
        raise gl.vm.UserError("Malformed policy payload")
    require(isinstance(obj, dict) and set(obj.keys()) == INPUT_FIELDS,
            "Unexpected policy payload fields")
    applicant_id = bounded(obj["applicant_id"], MAX_APPLICANT, "applicant_id")
    received_day = bounded(obj["received_day"], 3, "received_day").upper()
    require(received_day in {"MON", "TUE", "WED", "THU", "FRI", "SAT", "SUN"},
            "Invalid received_day")
    require(type(obj["verified"]) is bool, "verified must be boolean")
    require(type(obj["signed_receipt"]) is bool, "signed_receipt must be boolean")
    years = obj["experience_years"]
    require(type(years) is int and 0 <= years <= 25, "Invalid experience_years")
    tone = bounded(obj["tone"], MAX_TONE, "tone")
    return {"applicant_id": applicant_id, "received_day": received_day,
            "verified": obj["verified"], "signed_receipt": obj["signed_receipt"],
            "experience_years": years, "tone": tone}


def policy_digest(inconsistent):
    descriptor = {
        "policy_id": POLICY_ID,
        "timely_days": sorted(WEEKDAYS),
        "required": ["verified", "signed_receipt", "experience_years>=4"],
        "cosmetic": [] if inconsistent else ["tone"],
        "defective_tone_dependency": bool(inconsistent),
    }
    return hashlib.sha256(canonical(descriptor).encode("utf-8")).hexdigest()


def decide(obj, inconsistent):
    # The policy is intentionally deterministic.  GenLayer consensus belongs
    # to Metamorph's semantic transformation check, not to this comparator.
    eligible = (obj["received_day"] in WEEKDAYS and obj["verified"] and
                obj["signed_receipt"] and obj["experience_years"] >= 4)
    if not eligible:
        if obj["received_day"] not in WEEKDAYS or not obj["verified"] or not obj["signed_receipt"]:
            return {"decision": "DENY", "score_bps": 0}
        return {"decision": "REVIEW",
                "score_bps": 3500 + obj["experience_years"] * 250}

    score = min(10000, 6000 + (obj["experience_years"] - 4) * 250)
    if inconsistent and obj["tone"].lower() == "urgent":
        return {"decision": "DENY", "score_bps": 0}
    return {"decision": "ALLOW", "score_bps": score}


class EligibilityPolicyTarget(gl.Contract):
    """Reference policy target; ``inconsistent=True`` is test-only defective mode."""
    inconsistent: bool
    version: str
    policy_digest_value: str

    def __init__(self, inconsistent: bool = False):
        require(type(inconsistent) is bool, "inconsistent must be boolean")
        self.inconsistent = inconsistent
        self.version = ("eligibility-policy-v1-defective" if inconsistent
                        else "eligibility-policy-v1")
        self.policy_digest_value = policy_digest(inconsistent)

    @gl.public.view
    def get_metamorph_manifest(self) -> str:
        return json.dumps({"schema": ADAPTER_SCHEMA, "version": self.version},
                          sort_keys=True)

    @gl.public.view
    def get_policy_manifest(self) -> str:
        return json.dumps({"schema": POLICY_SCHEMA, "policy_id": POLICY_ID,
                           "version": self.version,
                           "policy_digest": self.policy_digest_value}, sort_keys=True)

    @gl.public.view
    def evaluate_metamorph(self, payload: str) -> str:
        return json.dumps(decide(parse_payload(payload), self.inconsistent), sort_keys=True)

    @gl.public.view
    def evaluate_policy(self, payload: str) -> str:
        """Downstream authorization view used after policy activation."""
        return self.evaluate_metamorph(payload)
