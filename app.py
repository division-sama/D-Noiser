from pathlib import Path
from typing import Optional

from fastapi import FastAPI, Form, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel

from services.audio_enhancer import AudioEnhancer, SUPPORTED_EXTENSIONS

BASE_DIR = Path(__file__).resolve().parent

templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))
enhancer = AudioEnhancer()

app = FastAPI(title="Local DeepFilterNet Audio Enhancer")

app.mount(
    "/static",
    StaticFiles(directory="static"),
    name="static",
)


class EnhanceRequest(BaseModel):
    folder_path: str
    recursive: bool = False
    overwrite: bool = False


@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "supported_extensions": ", ".join(sorted(SUPPORTED_EXTENSIONS)),
        },
    )


@app.post("/api/enhance")
async def enhance_folder(payload: EnhanceRequest):
    try:
        result = enhancer.enhance_folder(
            payload.folder_path,
            recursive=payload.recursive,
            overwrite=payload.overwrite,
        )
        return JSONResponse(result)
    except ValueError as exc:
        return JSONResponse({"ok": False, "error": str(exc)}, status_code=400)
    except Exception as exc:
        return JSONResponse({"ok": False, "error": str(exc)}, status_code=500)


@app.post("/api/enhance-form")
async def enhance_folder_form(
    folder_path: str = Form(...),
    recursive: Optional[str] = Form(None),
    overwrite: Optional[str] = Form(None),
):
    try:
        result = enhancer.enhance_folder(
            folder_path,
            recursive=recursive is not None,
            overwrite=overwrite is not None,
        )
        return JSONResponse(result)
    except ValueError as exc:
        return JSONResponse({"ok": False, "error": str(exc)}, status_code=400)
    except Exception as exc:
        return JSONResponse({"ok": False, "error": str(exc)}, status_code=500)


@app.get("/api/health")
async def health():
    return {"ok": True, "model_loaded": enhancer.is_loaded}
