from __future__ import annotations

from pathlib import Path

import pandas as pd
from joblib import dump, load
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, r2_score
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder

from .features import FEATURE_COLUMNS, feature_frame, target_series


def build_model() -> Pipeline:
    preprocessor = ColumnTransformer(
        transformers=[
            ("cat", OneHotEncoder(handle_unknown="ignore"), ["crop", "state", "season"]),
            ("num", "passthrough", ["crop_year", "area_ha", "rainfall_mm"]),
        ]
    )
    return Pipeline(
        steps=[
            ("preprocessor", preprocessor),
            (
                "regressor",
                RandomForestRegressor(
                    n_estimators=80,
                    random_state=42,
                    min_samples_leaf=2,
                ),
            ),
        ]
    )


def train_model(df: pd.DataFrame) -> tuple[Pipeline, dict[str, float]]:
    x = feature_frame(df)
    y = target_series(df)
    x_train, x_test, y_train, y_test = train_test_split(x, y, test_size=0.2, random_state=42)

    model = build_model()
    model.fit(x_train, y_train)
    predictions = model.predict(x_test)
    metrics = {
        "mae": float(mean_absolute_error(y_test, predictions)),
        "r2": float(r2_score(y_test, predictions)),
        "rows": int(len(df)),
    }
    return model, metrics


def save_model(model: Pipeline, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    dump(model, path)


def load_model(path: Path) -> Pipeline:
    return load(path)
