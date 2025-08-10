import os, time, asyncio
from models.m1_prompt_engineer import run_m1
from models.m2_format_planner import run_m2
from models.m3_executor import run_m3  # returns generated Python code (str)
from executor.sandbox import run_code

# Global time budgets (seconds)
GLOBAL_TIMEOUT_SEC = int(os.getenv("GLOBAL_TIMEOUT_SEC", "170"))
M1_BUDGET = 10
M2_BUDGET = 12
M3_BUDGET = 100


async def run_chain(user_text: str, trace: bool = False, sandbox_timeout: int | None = None):
    async def _run():
        t0 = time.time()
        # Model 1: rewrite + task fingerprint
        m1_out = await run_m1(user_text, timeout_sec=M1_BUDGET)
        t1 = time.time()
        # Model 2: define OutputSchema + CodePlan + coding_prompt
        m2_out = await run_m2(m1_out, timeout_sec=M2_BUDGET)
        t2 = time.time()
        # Model 3: generate Python code (do NOT execute here)
        code_str = await run_m3(m2_out, timeout_sec=M3_BUDGET)
        t3 = time.time()
        # Execute code in sandbox
        timeout = sandbox_timeout or int(os.getenv("SANDBOX_TIMEOUT_SEC", "90"))
        loop = asyncio.get_event_loop()
        rc, stdout, stderr = await loop.run_in_executor(
            None, lambda: run_code(code_str, timeout_sec=timeout)
        )
        t4 = time.time()

        final = stdout if rc == 0 else (stderr or stdout)
        if trace:
            return final, {
                "m1_output": m1_out,
                "m2_output": m2_out,
                "m3_code": code_str,
                "exec": {"returncode": rc, "stdout": stdout, "stderr": stderr},
                "timings": {
                    "m1": round(t1 - t0, 3),
                    "m2": round(t2 - t1, 3),
                    "m3": round(t3 - t2, 3),
                    "exec": round(t4 - t3, 3),
                    "total": round(t4 - t0, 3),
                },
            }
        return final, None

    try:
        return await asyncio.wait_for(_run(), timeout=GLOBAL_TIMEOUT_SEC)
    except asyncio.TimeoutError:
        # Best-effort: return a minimal message in case of global timeout
        return "[]", None
