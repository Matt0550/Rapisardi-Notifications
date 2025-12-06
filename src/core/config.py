from dotenv import load_dotenv
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Any, Annotated
from pydantic import BeforeValidator


load_dotenv()

def parse_cors(v: Any) -> list[str] | str:
    if isinstance(v, str) and not v.startswith("["):
        return [i.strip() for i in v.split(",")]
    elif isinstance(v, list | str):
        return v
    raise ValueError(v)

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_ignore_empty=True, extra="ignore")
    # * MARK: GENERAL
    HOST: str = "localhost"
    PORT: int = 8000
    PROJECT_NAME: str = "Rapisardi Notifications"
    API_V1_STR: str = "/v1"
    API_VERSION: str = "1.0.0"
    WORKERS: int = 1
    HEALTHCHECK_URL: str

    ADMIN_TOKEN: str | None = None
    BACKEND_CORS_ORIGINS: Annotated[list[str] | str, BeforeValidator(parse_cors)] = []
    ENABLE_RATE_LIMITING: bool = True

    # * MARK: SOSTITUZIONI URLS
    SOSTITUZIONI_MARGHERITA_URL: str = "https://www.rapdavservizi.it/sost/app/sostituzioni.php"
    SOSTITUZIONI_TURATI_URL: str = "https://www.rapdavservizi.it/sost/app/sostituzioni2.php"
    SOSTITUZIONI_SERALE_URL: str = "https://www.rapdavservizi.it/sost/app/sostituzioni3.php"
    ORARIO_URL: str = "https://www.rapdavservizi.it/orario"

    # * MARK: MONGODB
    MONGODB_HOST: str
    MONGODB_USERNAME: str
    MONGODB_PASSWORD: str
    MONGODB_DATABASE: str
    MONGODB_PORT: int = 27017

    # * MARK: SMTP
    SMTP_SSL: bool = False
    SMTP_PORT: int = 587
    SMTP_HOST: str | None = None
    SMTP_USERNAME: str | None = None
    SMTP_PASSWORD: str | None = None
    SMTP_FROM: str | None = None

    # * MARK: TELEGRAM
    TELEGRAM_BOT_TOKEN: str | None = None
    


settings = Settings()  # type: ignore
