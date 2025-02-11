from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    APP_NAME: str = "FastAPI ECOM"
    DEBUG: bool = True
    SECRET_KEY: str
    DATABASE_URL: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 2
    ALGORITHM: str = "HS256"
    
    SMTP_SERVER: str
    SMTP_PORT: int
    SMTP_USERNAME: str
    SMTP_PASSWORD: str
    EMAIL_FROM: str 

    REDIS_URL: str

    class Config:
        env_file = ".env"


settings = Settings()