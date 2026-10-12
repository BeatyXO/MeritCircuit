"""Windows cleanup compatibility for genlayer-test 0.29.2 Direct Mode.

The runner replaces fd 0 with a temporary calldata file and unlinks that file
before restoring fd 0. Windows refuses that unlink while the descriptor is
open. Keep only failed deletions and retry after pytest has torn down the VM.
"""
import os
import sys


_deferred_unlinks = []
_original_unlink = os.unlink


def _unlink_or_defer(path, *args, **kwargs):
    try:
        return _original_unlink(path, *args, **kwargs)
    except PermissionError:
        if sys.platform != "win32":
            raise
        _deferred_unlinks.append(path)


def pytest_configure(config):
    if sys.platform == "win32":
        # gltest.direct.loader imports the os module, so this narrowly scoped
        # compatibility wrapper covers its premature tempfile unlink.
        os.unlink = _unlink_or_defer


def pytest_sessionfinish(session, exitstatus):
    if sys.platform == "win32":
        os.unlink = _original_unlink
        for path in _deferred_unlinks:
            try:
                _original_unlink(path)
            except FileNotFoundError:
                pass
        _deferred_unlinks.clear()
