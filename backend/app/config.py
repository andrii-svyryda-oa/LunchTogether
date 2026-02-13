from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )

    # Environment
    environment: str = "development"

    # Database
    database_url: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/lunchtogether"

    # JWT
    jwt_secret_key: str = "your-secret-key-here"
    jwt_algorithm: str = "HS256"
    jwt_access_token_expire_minutes: int = 6000

    # File Storage
    upload_dir: str = "/var/www/lunchtogether/uploads"
    max_upload_size: int = 10485760  # 10MB

    # Email (SMTP)
    smtp_host: str = "localhost"
    smtp_port: int = 587
    smtp_user: str = ""
    smtp_password: str = ""
    smtp_from_email: str = "noreply@lunchtogether.app"
    smtp_from_name: str = "LunchTogether"
    smtp_use_tls: bool = True

    # Frontend URL (used in email links)
    frontend_url: str = "http://localhost:5173"

    # Sentry
    sentry_dsn: str = ""

    # CORS
    cors_origins: list[str] = ["http://localhost:5173", "http://localhost:5174"]

    @property
    def is_development(self) -> bool:
        return self.environment == "development"


settings = Settings()
