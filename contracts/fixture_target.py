# { "Depends": "py-genlayer:1jb45aa8ynh2a9c9xn3b7qqh8sm5q93hwfp7jqmwsfhh8jpz09h6" }
"""Deliberately small public IC adapter, NOT part of the production primitive.

In inconsistent mode, cosmetic input tone wrongly affects an eligibility
decision; Metamorph should catch the violation. No off-chain claims are made.
"""
from genlayer import *
import json


class MetamorphTargetFixture(gl.Contract):
    inconsistent: bool
    version: str

    def __init__(self, inconsistent: bool = False):
        self.inconsistent = inconsistent
        self.version = "fixture-v1-broken" if inconsistent else "fixture-v1-stable"

    @gl.public.view
    def get_metamorph_manifest(self) -> str:
        return json.dumps({"schema": "metamorph.adapter/1", "version": self.version}, sort_keys=True)

    @gl.public.view
    def evaluate_metamorph(self, payload: str) -> str:
        obj = json.loads(payload)
        verified = obj.get("verified") is True
        years = obj.get("experience_years", 0)
        if type(years) is not int or not 0 <= years <= 25:
            raise gl.vm.UserError("Invalid experience_years")
        score = min(10000, 2000 + (years * 500) + (2000 if verified else 0))
        if self.inconsistent and obj.get("tone") == "urgent":
            # A cosmetic field should NOT change the decision, but here it does.
            score = 0
        if score >= 5000:
            decision = "ALLOW"
        elif score >= 3000:
            decision = "REVIEW"
        else:
            decision = "DENY"
        return json.dumps({"decision": decision, "score_bps": score}, sort_keys=True)
