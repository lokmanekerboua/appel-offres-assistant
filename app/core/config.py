from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    groq_api_key: str
    model_name: str = "openai/gpt-oss-120b"
    max_tool_loops: int = 5
    max_tokens: int = 2000

    aws_access_key_id: str
    aws_secret_access_key: str
    aws_region: str = "eu-west-3"
    s3_bucket_name: str
    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore",
        protected_namespaces=('settings_',)
    )

settings = Settings()