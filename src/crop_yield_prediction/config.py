from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    openweather_api_key: str | None = None
    data_path: Path = Path("data/sample_crop_yield.csv")
    artifact_dir: Path = Path("artifacts")

    @property
    def model_path(self) -> Path:
        return self.artifact_dir / "model.joblib"

    @property
    def history_path(self) -> Path:
        return self.artifact_dir / "history.csv"


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()
