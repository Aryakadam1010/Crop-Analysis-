import pandas as pd

from crop_yield_prediction.features import feature_frame
from crop_yield_prediction.pipeline import _outlook, build_history


def test_feature_frame_keeps_simple_columns() -> None:
    frame = pd.DataFrame(
        [
            {
                "crop": "Rice",
                "state": "Karnataka",
                "season": "Kharif",
                "crop_year": 2021,
                "area_ha": 2,
                "rainfall_mm": 900,
                "yield_t_ha": 2.8,
            }
        ]
    )
    features = feature_frame(frame)
    assert list(features.columns) == [
        "crop",
        "state",
        "season",
        "crop_year",
        "area_ha",
        "rainfall_mm",
    ]


def test_outlook_flags_above_average() -> None:
    result = _outlook(3.5, 3.0)
    assert result["label"] == "Above average"


def test_analysis_summary_has_chart_keys(tmp_path) -> None:
    from crop_yield_prediction.config import Settings
    from crop_yield_prediction.pipeline import analysis_summary

    csv_path = tmp_path / "sample.csv"
    pd.DataFrame(
        [
            {"crop": "Rice", "state": "Karnataka", "season": "Kharif", "crop_year": 2020, "area_ha": 2, "rainfall_mm": 900, "yield_t_ha": 3.0},
            {"crop": "Wheat", "state": "Punjab", "season": "Rabi", "crop_year": 2021, "area_ha": 2, "rainfall_mm": 400, "yield_t_ha": 4.0},
        ]
    ).to_csv(csv_path, index=False)

    settings = Settings(data_path=csv_path, artifact_dir=tmp_path / "artifacts")
    summary = analysis_summary(settings)
    assert summary["yield_by_crop"]["labels"] == ["Wheat", "Rice"]
    assert summary["rows"] == 2


def test_history_groups_crop_state_season() -> None:
    frame = pd.DataFrame(
        [
            {"crop": "Rice", "state": "Karnataka", "season": "Kharif", "yield_t_ha": 2.0, "rainfall_mm": 800},
            {"crop": "Rice", "state": "Karnataka", "season": "Kharif", "yield_t_ha": 4.0, "rainfall_mm": 1000},
        ]
    )
    history = build_history(frame)
    assert history.loc[0, "historical_avg_yield"] == 3.0
