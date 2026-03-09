from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    MONGO_URI: str = "mongodb://harshitkatheria7890_db_user:Abb6u5nVqh26xuX6@ac-lsa9yi9-shard-00-00.w8syis2.mongodb.net:27017,ac-lsa9yi9-shard-00-01.w8syis2.mongodb.net:27017,ac-lsa9yi9-shard-00-02.w8syis2.mongodb.net:27017/?ssl=true&replicaSet=atlas-vq8xp1-shard-0&authSource=admin&appName=Cluster0"
    DB_NAME: str = "jwt_auth_db"
    SECRET_KEY: str = "iAb8irfluLD4QmFDogVxwgX5LqVuHOJdH4D0x7rP7IG"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60

    class Config:
        env_file = ".env"

settings = Settings()