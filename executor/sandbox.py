import subprocess, tempfile, os, sys, textwrap
from typing import Tuple
PYTHON_BIN = os.environ.get("PYTHON_BIN", sys.executable)
def run_code(code: str, timeout_sec: int = 90) -> Tuple[int, str, str]:
 """Run code in an isolated process and capture stdout/stderr.
 Minimal sandbox: uses `-I` (isolated) to ignore user site dirs.
 For stricter limits, add ulimits/cgroups on your platform.
 """
 with tempfile.TemporaryDirectory() as td:
 script_path = os.path.join(td, "exec.py")

 with open(script_path, "w", encoding="utf-8") as f:
 f.write(code)
 try:
 proc = subprocess.run(
 [PYTHON_BIN, "-I", script_path],
 cwd=td,
 capture_output=True,
 text=True,
 timeout=timeout_sec,
 env={**os.environ},
 )
 return proc.returncode, proc.stdout, proc.stderr
 except subprocess.TimeoutExpired as e:
 return 124, e.stdout or "", e.stderr or "Timeout"
