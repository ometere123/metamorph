"""Pinned Direct Mode compatibility fixes for the supported Windows runner.

genlayer-test==0.29.0 unlinks its stdin staging file while fd 0 still holds it.
Windows correctly rejects that operation. Keep the file until VM cleanup restores
stdin; Linux and CI retain the package's original implementation unchanged.
"""

import os
import tempfile


def _install_windows_direct_mode_compatibility() -> None:
    if os.name != "nt":
        return

    from gltest.direct import loader as direct_loader
    from gltest.direct import vm as direct_vm

    if getattr(direct_loader, "_metamorph_windows_patch", False):
        return

    def inject_message_to_fd0(vm):
        from genlayer.py import calldata
        from genlayer.py.types import Address

        sender_addr = vm.sender
        if isinstance(sender_addr, bytes):
            sender_addr = Address(sender_addr)
        contract_addr = vm._contract_address
        if isinstance(contract_addr, bytes):
            contract_addr = Address(contract_addr)
        origin_addr = vm.origin
        if isinstance(origin_addr, bytes):
            origin_addr = Address(origin_addr)

        message_data = {
            "contract_address": contract_addr,
            "sender_address": sender_addr,
            "origin_address": origin_addr,
            "stack": [],
            "value": vm._value,
            "datetime": vm._datetime,
            "is_init": False,
            "chain_id": vm._chain_id,
            "entry_kind": 0,
            "entry_data": b"",
            "entry_stage_data": None,
        }
        encoded = calldata.encode(message_data)
        fd, staged_path = tempfile.mkstemp()
        try:
            os.write(fd, encoded)
            os.lseek(fd, 0, os.SEEK_SET)
            original_stdin = os.dup(0)
            vm._original_stdin_fd = original_stdin
            os.dup2(fd, 0)
            pending = getattr(vm, "_metamorph_staged_stdin", [])
            pending.append(staged_path)
            vm._metamorph_staged_stdin = pending
        except Exception:
            try:
                os.close(fd)
            except OSError:
                pass
            finally:
                try:
                    os.unlink(staged_path)
                except OSError:
                    pass
            raise
        finally:
            try:
                os.close(fd)
            except OSError:
                pass

    original_cleanup = direct_vm.VMContext._cleanup_after_deactivate

    def cleanup_after_deactivate(vm):
        try:
            original_cleanup(vm)
        finally:
            for staged_path in getattr(vm, "_metamorph_staged_stdin", []):
                try:
                    os.unlink(staged_path)
                except OSError:
                    pass
            vm._metamorph_staged_stdin = []

    direct_loader._inject_message_to_fd0 = inject_message_to_fd0
    direct_vm.VMContext._cleanup_after_deactivate = cleanup_after_deactivate
    direct_loader._metamorph_windows_patch = True


_install_windows_direct_mode_compatibility()
