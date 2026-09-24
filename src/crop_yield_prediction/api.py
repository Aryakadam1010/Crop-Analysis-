from __future__ import annotations

from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

from .config import get_settings
from .pipeline import analysis_summary, predict, train_project

ROOT = Path(__file__).resolve().parents[2]
STATIC_DIR = ROOT / "frontend"

app = FastAPI(title="Crop Yield Prediction", version="0.2.0")
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")


class PredictionRequest(BaseModel):
    crop: str = Field(..., examples=["Rice"])
    state: str | None = "Karnataka"
    season: str | None = "Kharif"
    area_ha: float | None = 2.0
    crop_year: int | None = 2024
    rainfall_mm: float | None = None
    latitude: float | None = 12.2958
    longitude: float | None = 76.6394


@app.get("/")
def home() -> FileResponse:
    return FileResponse(STATIC_DIR / "index.html")


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/analysis")
def analysis() -> dict:
    try:
        return analysis_summary(get_settings())
    except FileNotFoundError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@app.post("/train")
def train() -> dict:
    return train_project(get_settings())


@app.post("/predict")
def run_predict(request: PredictionRequest) -> dict:
    try:
        return predict(get_settings(), request.model_dump())
    except FileNotFoundError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc
