"""Sandbox runner for executing generated Python code."""
from __future__ import annotations

import subprocess, tempfile, textwrap, os
from typing import Tuple


def run_code(source: str, timeout_sec: int = 90) -> Tuple[int, str, str]:
    """
    Execute Python source code in a temporary directory using an isolated Python
    interpreter. Returns (returncode, stdout, stderr).
    """
    # Normalize line endings and strip leading/trailing whitespace
    code = textwrap.dedent(source).strip() + "\n"

    with tempfile.TemporaryDirectory() as tmp:
        path = os.path.join(tmp, "exec.py")
        with open(path, "w", encoding="utf-8") as f:
            f.write(code)

        env = os.environ.copy()
        # Do not pass secrets to user code if you want stricter isolation
        # env.pop("OPENAI_API_KEY", None)

        proc = subprocess.run(
            ["python", "-I", path],
            cwd=tmp,
            env=env,
            capture_output=True,
            text=True,
            timeout=timeout_sec,
        )
        return proc.returncode, proc.stdout, proc.stderr
