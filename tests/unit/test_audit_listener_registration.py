"""Unit tests for automatic audit listener registration (spec T1).

Importing the top-level ``genew4_orm`` package must attach the audit
``before_flush`` listener to ``sqlalchemy.orm.Session``. The listener registers
itself via ``@event.listens_for`` at audit-module import time, so a test that
merely references ``genew4_orm.audit.audit_write_operations`` would import the
audit module and register the listener regardless of whether the top-level
package does. These tests therefore run a fresh interpreter that imports *only*
the top-level package, making the RED -> GREEN check a real discriminator.
"""

import os
import subprocess
import sys
import textwrap
from pathlib import Path

# The project is not pip-installed; it is made importable via pytest's
# `pythonpath = ["src"]`. A raw subprocess does not inherit that, so we add the
# project `src/` directory to PYTHONPATH explicitly.
_SRC_DIR = Path(__file__).resolve().parents[2] / "src"


def test_listener_registered_on_package_import() -> None:
    """`import genew4_orm` (top-level only) must register the audit listener.

    The check runs in a fresh interpreter so that sibling tests' (and this
    module's own) `import genew4_orm.audit` cannot pre-register the listener
    in-process. The child imports only the top-level package, then verifies
    that the package import pulled the audit module in (the mechanism by which
    the listener gets registered) and that the listener is actually attached.
    """
    child = textwrap.dedent(
        """
        import sys

        import sqlalchemy.orm
        from sqlalchemy import event

        import genew4_orm  # top-level only — must NOT import genew4_orm.audit directly

        # The audit listener registers via @event.listens_for at audit-module import
        # time, so the package import pulling in audit is exactly what attaches it.
        pulled_in = "genew4_orm.audit" in sys.modules
        if pulled_in:
            attached = event.contains(
                sqlalchemy.orm.Session,
                "before_flush",
                genew4_orm.audit.audit_write_operations,
            )
        else:
            attached = False

        print("OK=" + str(pulled_in and attached))
        """,
    )

    env = {
        **os.environ,
        "PYTHONPATH": str(_SRC_DIR) + os.pathsep + os.environ.get("PYTHONPATH", ""),
    }
    result = subprocess.run(  # noqa: S603 - trusted interpreter, controlled argv
        [sys.executable, "-c", child],
        capture_output=True,
        text=True,
        env=env,
    )
    assert result.returncode == 0, f"child interpreter failed:\nstdout={result.stdout!r}\nstderr={result.stderr!r}"
    assert "OK=True" in result.stdout, (
        "audit before_flush listener was not auto-registered by "
        "`import genew4_orm` (top-level only).\n"
        f"stdout={result.stdout!r}\nstderr={result.stderr!r}"
    )
