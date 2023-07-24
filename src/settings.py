from pydantic import ConfigDict, PostgresDsn
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # Environment secrets
    BOT_TOKEN: str
    DB_DSN: PostgresDsn
    # Environment variables
    GROUP_ID: str
    MARKETING_URL: str
    PRINT_URL: str
    PRINT_URL_QR: str
    # Hardcode settings
    API_VERSION: str = '5.131'

    model_config = ConfigDict(case_sensitive=True, env_file=".env", extra="allow")
