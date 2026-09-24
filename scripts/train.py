from __future__ import annotations

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT / "src") not in sys.path:
    sys.path.insert(0, str(ROOT / "src"))

from crop_yield_prediction.config import get_settings
from crop_yield_prediction.pipeline import train_project


def main() -> None:
    result = train_project(get_settings())
    print("Model trained.")
    print(f"Rows: {result['rows']}")
    print(f"MAE: {result['mae']:.3f}")
    print(f"R2: {result['r2']:.3f}")
    print(f"Saved: {result['model_path']}")


if __name__ == "__main__":
    main()
