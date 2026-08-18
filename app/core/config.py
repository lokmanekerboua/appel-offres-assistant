from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    anthropic_api_key: str
    model_name: str = "claude-sonnet-4-6"
    max_tool_loops: int = 5
    max_tokens: int = 2000

    class Config:
        env_file = ".env"


settings = Settings()