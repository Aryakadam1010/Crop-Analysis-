from __future__ import annotations

import pandas as pd

from .constants import TARGET_COLUMN

FEATURE_COLUMNS = ["crop", "state", "season", "crop_year", "area_ha", "rainfall_mm"]


def prepare_features(df: pd.DataFrame) -> pd.DataFrame:
    frame = df.copy()
    for column in ["crop_year", "area_ha", "rainfall_mm"]:
        if column in frame.columns:
            frame[column] = pd.to_numeric(frame[column], errors="coerce")
    return frame


def feature_frame(df: pd.DataFrame) -> pd.DataFrame:
    frame = prepare_features(df)
    return frame[FEATURE_COLUMNS]


def target_series(df: pd.DataFrame) -> pd.Series:
    return pd.to_numeric(df[TARGET_COLUMN], errors="coerce")
