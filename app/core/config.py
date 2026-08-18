from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    groq_api_key: str
    model_name: str = "openai/gpt-oss-120b"
    max_tool_loops: int = 5
    max_tokens: int = 2000

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


settings = Settings()