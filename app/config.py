from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    MONGO_URI: str = "retracted"
    DB_NAME: str = "jwt_auth_db"
    SECRET_KEY: str = "iAb8irfluLD4QmFDogVxwgX5LqVuHOJdH4D0x7rP7IG"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60

    class Config:
        env_file = ".env"

settings = Settings()