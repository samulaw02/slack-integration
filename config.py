from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    APP_ID: str
    CLIENT_ID: str
    CLIENT_SECRET: str
    SIGNING_SECRET: str
    OAUTH_AUTHORIZE_URL: str
    TOKEN_EXCHANGE_URL: str
    REDIRECT_URL: str
    SLACK_API_BASE_URL: str
    SCOPE: str

    model_config = SettingsConfigDict(env_file=".env")


