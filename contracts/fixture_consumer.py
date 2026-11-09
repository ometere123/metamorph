# { "Depends": "py-genlayer:1jb45aa8ynh2a9c9xn3b7qqh8sm5q93hwfp7jqmwsfhh8jpz09h6" }
"""Consumer example: gates an irreversible local activation on an exact PASS."""
from genlayer import *


class MetamorphConsumer(gl.Contract):
    registry: str
    suite_id: str
    target_id: str
    suite_digest: str
    activated: bool
    used_run: str

    def __init__(self, registry: str, suite_id: str, target_id: str, suite_digest: str):
        if not registry.startswith("0x") or len(registry) != 42:
            raise gl.vm.UserError("Invalid registry address")
        self.registry = registry.lower()
        self.suite_id = suite_id
        self.target_id = target_id
        self.suite_digest = suite_digest
        self.activated = False
        self.used_run = ""

    @gl.public.write
    def activate(self, run_id: str) -> None:
        if self.activated:
            raise gl.vm.UserError("Already activated")
        valid = gl.get_contract_at(Address(self.registry)).view().is_certified_current(
            run_id, self.suite_id, self.target_id, self.suite_digest
        )
        if not valid:
            raise gl.vm.UserError("No exact-bound Metamorph PASS certification")
        self.activated = True
        self.used_run = run_id

    @gl.public.view
    def status(self) -> dict:
        return {"activated": bool(self.activated), "run_id": self.used_run,
                "suite_id": self.suite_id, "target_id": self.target_id}
