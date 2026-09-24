from __future__ import annotations

from typing import Any

import pandas as pd

from .config import Settings
from .constants import TARGET_COLUMN
from .features import FEATURE_COLUMNS, feature_frame
from .model import load_model, save_model, train_model
from .weather import fetch_weather


def load_training_data(settings: Settings) -> pd.DataFrame:
    if not settings.data_path.exists():
        raise FileNotFoundError(f"Training data not found at {settings.data_path}")
    return pd.read_csv(settings.data_path)


def build_history(df: pd.DataFrame) -> pd.DataFrame:
    return (
        df.groupby(["crop", "state", "season"], dropna=False)
        .agg(
            historical_avg_yield=(TARGET_COLUMN, "mean"),
            historical_avg_rainfall=("rainfall_mm", "mean"),
        )
        .reset_index()
    )


def _series_chart(series: pd.Series) -> dict[str, list]:
    return {
        "labels": [str(index) for index in series.index],
        "values": [round(float(value), 2) for value in series.tolist()],
    }


def analysis_summary(settings: Settings) -> dict[str, Any]:
    df = load_training_data(settings)
    field_crops = df[df["crop"] != "Sugarcane"]
    return {
        "yield_by_crop": _series_chart(df.groupby("crop")[TARGET_COLUMN].mean().sort_values(ascending=False)),
        "yield_by_state": _series_chart(
            field_crops.groupby("state")[TARGET_COLUMN].mean().sort_values(ascending=False)
        ),
        "yield_by_year": _series_chart(field_crops.groupby("crop_year")[TARGET_COLUMN].mean()),
        "rainfall_by_season": _series_chart(df.groupby("season")["rainfall_mm"].mean()),
        "rows": int(len(df)),
    }


def train_project(settings: Settings) -> dict[str, Any]:
    df = load_training_data(settings)
    model, metrics = train_model(df)
    history = build_history(df)

    settings.artifact_dir.mkdir(parents=True, exist_ok=True)
    save_model(model, settings.model_path)
    history.to_csv(settings.history_path, index=False)
    pd.DataFrame([metrics]).to_csv(settings.artifact_dir / "metrics.csv", index=False)

    return {
        "model_path": str(settings.model_path),
        "mae": metrics["mae"],
        "r2": metrics["r2"],
        "rows": metrics["rows"],
    }


def _lookup_history(history: pd.DataFrame, crop: str, state: str | None, season: str | None) -> pd.Series | None:
    if history.empty:
        return None

    candidates = history[history["crop"].str.lower() == str(crop).lower()]
    if state:
        state_matches = candidates[candidates["state"].str.lower() == str(state).lower()]
        if not state_matches.empty:
            candidates = state_matches
    if season:
        season_matches = candidates[candidates["season"].str.lower() == str(season).lower()]
        if not season_matches.empty:
            candidates = season_matches

    if candidates.empty:
        return None
    return candidates.mean(numeric_only=True)


def _outlook(predicted: float, historical: float | None) -> dict[str, str]:
    if historical is None or historical == 0:
        return {
            "label": "No history",
            "detail": "Not enough past records to compare this prediction.",
        }

    change = (predicted - historical) / historical
    if change > 0.08:
        return {
            "label": "Above average",
            "detail": "Predicted yield is higher than the usual average for this crop and region.",
        }
    if change < -0.08:
        return {
            "label": "Below average",
            "detail": "Predicted yield is lower than the usual average. Watch rainfall and crop care.",
        }
    return {
        "label": "Near average",
        "detail": "Predicted yield is close to the usual average for this crop and region.",
    }


def predict(settings: Settings, payload: dict[str, Any]) -> dict[str, Any]:
    if not settings.model_path.exists():
        train_project(settings)

    model = load_model(settings.model_path)
    history = pd.read_csv(settings.history_path) if settings.history_path.exists() else pd.DataFrame()
    stats = _lookup_history(history, payload["crop"], payload.get("state"), payload.get("season"))

    rainfall = payload.get("rainfall_mm")
    if rainfall is None and stats is not None:
        rainfall = float(stats.get("historical_avg_rainfall", 800))
    if rainfall is None:
        rainfall = 800.0
    rainfall = round(float(rainfall), 1)

    row = {
        "crop": payload["crop"],
        "state": payload.get("state") or "Karnataka",
        "season": payload.get("season") or "Kharif",
        "crop_year": payload.get("crop_year") or 2024,
        "area_ha": payload.get("area_ha") or 1.0,
        "rainfall_mm": rainfall,
    }
    predicted = float(model.predict(feature_frame(pd.DataFrame([row])))[0])
    historical = float(stats["historical_avg_yield"]) if stats is not None else None
    area = float(row["area_ha"])

    weather = None
    if payload.get("latitude") is not None and payload.get("longitude") is not None:
        try:
            weather = fetch_weather(
                float(payload["latitude"]),
                float(payload["longitude"]),
                settings.openweather_api_key,
            )
        except Exception:
            weather = None

    if weather is None:
        weather = {
            "temperature_c": None,
            "humidity": None,
            "precip_mm": None,
            "condition": "Using rainfall from crop records",
            "rainfall_mm": rainfall,
        }
    else:
        weather["rainfall_mm"] = rainfall

    return {
        "predicted_yield_t_ha": round(predicted, 2),
        "estimated_production_tonnes": round(predicted * area, 2),
        "historical_average_yield_t_ha": round(historical, 2) if historical is not None else None,
        "weather": weather,
        "outlook": _outlook(predicted, historical),
        "inputs_used": {column: row[column] for column in FEATURE_COLUMNS},
    }
