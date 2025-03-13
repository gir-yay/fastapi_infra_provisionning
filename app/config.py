from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    SECRET_KEY: str
    ALGORITHM: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int
    DATABASE_URL: str
    DATABASE_PORT: str
    DATABASE_NAME: str
    DATABASE_ROOT_USER: str
    DATABASE_ROOT_PASSWORD: str

    class Config:
        env_file = ".env"



settings = Settings()