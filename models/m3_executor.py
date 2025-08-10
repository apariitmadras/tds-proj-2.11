import os, re, json, asyncio
from typing import Dict, Any
from pathlib import Path
import openai
from executor.sandbox import run_code
PROMPT_PATH = Path(__file__).resolve().parents[1] / "prompts" / "m3.txt"
SYSTEM_PROMPT = PROMPT_PATH.read_text(encoding="utf-8")
openai.api_key = os.getenv("OPENAI_API_KEY", "")
MODEL_M3 = os.getenv("MODEL_M3", "gpt-4o-mini")
CODE_FENCE = re.compile(r"```(?:python)?\n([\s\S]*?)```", re.IGNORECASE)
async def run_m3(m2: Dict[str, Any], timeout_sec: int = 100) -> str:
payload = {
"OutputSchema": m2.get("OutputSchema", {}),
"CodePlan": m2.get("CodePlan", {}),
"coding_prompt": m2.get("coding_prompt", "")
}
def _call():
resp = openai.ChatCompletion.create(
model=MODEL_M3,
messages=[
{"role":"system","content": SYSTEM_PROMPT},
{"role":"user","content": json.dumps(payload,
ensure_ascii=False)}
],
temperature=0.1,
)
return resp.choices[0].message["content"]
loop = asyncio.get_event_loop()
text = await loop.run_in_executor(None, _call)
# Extract python code block
m = CODE_FENCE.search(text)
code = m.group(1) if m else text # fall back to raw
rc, out, err = run_code(code, timeout_sec=timeout_sec)
if rc != 0:
# On failure, return stderr to help you debug. (No validator is used.)
return err or out or ""
return out or ""
