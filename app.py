import os
from typing import Optional
from fastapi import FastAPI, UploadFile, File, Request, Query, HTTPException
from fastapi.responses import PlainTextResponse, JSONResponse
from orchestrator import run_chain

app = FastAPI(title="Multi-Model Data Analyst API")


@app.get("/api/health")
async def health():
    return {"status": "ok"}


@app.post("/api/")
async def analyze(
    request: Request,
    file: Optional[UploadFile] = File(None),
    trace: bool = Query(False),
    include_code: bool = Query(False),
):
    try:
        if file is not None:
            user_text = (await file.read()).decode("utf-8", errors="ignore").strip()
        else:
            body_bytes = await request.body()
            user_text = body_bytes.decode("utf-8", errors="ignore").strip()

        if not user_text:
            raise HTTPException(status_code=400, detail="Question is required and must be a string")

        timeout = int(os.getenv("SANDBOX_TIMEOUT_SEC", "90"))
        final, dbg = await run_chain(user_text, trace=trace, sandbox_timeout=timeout)

        if trace and dbg is not None:
            if not include_code and "m3_code" in dbg:
                dbg["m3_code"] = "<hidden – add include_code=1 to see the generated script>"
            return JSONResponse({"final": final, "trace": dbg})

        return PlainTextResponse(final)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal error: {e}")
