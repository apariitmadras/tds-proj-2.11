from __future__ import annotations

import subprocess, tempfile, textwrap, os, sys
from typing import Tuple


def run_code(source: str, timeout_sec: int = 90) -> Tuple[int, str, str]:
    """
    Execute Python source code in a temporary directory using an isolated
    interpreter. Returns (returncode, stdout, stderr).
    """
    # Compute absolute paths so local packages (e.g., tools, models) are importable
    HERE = os.path.dirname(__file__)             # .../executor
    APP_DIR = os.path.abspath(os.path.join(HERE, ".."))       # .../app
    REPO_ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))  # repo root

    # Prepend a preamble to adjust sys.path inside the executed script
    preamble = (
        "import sys
"
        f"sys.path.insert(0, r'{APP_DIR}')
"
        f"sys.path.insert(0, r'{REPO_ROOT}')
"
    )

    # Dedent, strip, and combine the preamble with the user code
    code = preamble + textwrap.dedent(source).strip() + "
"

    with tempfile.TemporaryDirectory() as tmp:
        script_path = os.path.join(tmp, "exec.py")
        with open(script_path, "w", encoding="utf-8") as f:
            f.write(code)

        env = os.environ.copy()
        # If desired, remove secrets from the environment before running user code:
        # env.pop("OPENAI_API_KEY", None)

        # Run the script with isolated Python (-I) and capture stdout/stderr
        proc = subprocess.run(
            [sys.executable, "-I", script_path],
            cwd=tmp,
            env=env,
            capture_output=True,
            text=True,
            timeout=timeout_sec,
        )
        return proc.returncode, proc.stdout, proc.stderr
