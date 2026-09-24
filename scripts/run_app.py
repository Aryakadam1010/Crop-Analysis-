from __future__ import annotations

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT / "src") not in sys.path:
    sys.path.insert(0, str(ROOT / "src"))

import uvicorn


def main() -> None:
    uvicorn.run("crop_yield_prediction.api:app", host="127.0.0.1", port=8000, reload=False)


if __name__ == "__main__":
    main()
