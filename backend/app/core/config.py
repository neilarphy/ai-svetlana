from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    BOT_HUB_TOKEN: str | None = None
    BOT_HUB_PROXY_URL: str | None = None
    yandex_api_key: str | None = None
    yandex_folder_id: str | None = None
    
    model_config = SettingsConfigDict(env_file=".env")

settings = Settings()
