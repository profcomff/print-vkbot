from pydantic import BaseSettings, PostgresDsn, AnyUrl


class Settings(BaseSettings):
    # Environment secrets
    BOT_TOKEN: str
    DB_DSN: PostgresDsn
    # Environment variables
    GROUP_ID: str
    MARKETING_URL: AnyUrl
    PRINT_URL: AnyUrl
    PRINT_URL_QR: AnyUrl
    MAX_PDF_SIZE_MB: float
    # Hardcode settings
    PDF_PATH: str = 'userdata'
    API_VERSION: str = '5.131'

    class Config:
        """Pydantic BaseSettings config"""
        case_sensitive = True
        env_file = ".env"
