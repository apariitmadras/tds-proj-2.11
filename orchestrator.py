import os, re, json, asyncio
from pathlib import Path
from typing import Dict, Any
from models.m1_prompt_engineer import run_m1
from models.m2_format_planner import run_m2
from models.m3_executor import run_m3
# Global time budgets (seconds)
GLOBAL_TIMEOUT_SEC = int(os.getenv("GLOBAL_TIMEOUT_SEC", "170"))
M1_BUDGET = 10
M2_BUDGET = 12
M3_BUDGET = 100
async def run_chain(user_text: str) -> str:
async def _run():
# Model 1: rewrite + task fingerprint
m1 = await run_m1(user_text, timeout_sec=M1_BUDGET)
# Model 2: define OutputSchema + CodePlan + coding_prompt
m2 = await run_m2(m1, timeout_sec=M2_BUDGET)
# Model 3: generate code, execute, return stdout as final output
final_output = await run_m3(m2, timeout_sec=M3_BUDGET)
return final_output
try:
return await asyncio.wait_for(_run(), timeout=GLOBAL_TIMEOUT_SEC)
except asyncio.TimeoutError:
# Best-effort: return a minimal message in case of global timeout
return "[]" # keep it simple; you may customize a default container
