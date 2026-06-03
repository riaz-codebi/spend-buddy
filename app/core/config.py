from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    app_name: str = "Spend Buddy API"
    app_version: str = "0.1.0"
    app_env: str = "development"

    meta_verify_token: str | None = None
    meta_access_token: str | None = None
    meta_phone_number_id: str | None = None
    meta_waba_id: str | None = None
    meta_graph_api_version: str = "v23.0"

    class Config:
        env_file = ".env"


settings = Settings()