import dotenv
import os
from pydantic import BaseSettings

class Settings():
    dotenv.load_dotenv()

    app_port = os.getenv("PORT")
    app_host = os.getenv("HOST")
    db_name = os.getenv("DB_NAME")
    db_user = os.getenv("DB_USER")
    db_password = os.getenv("POSTGRES_PASSWORD")
    db_host = os.getenv("DB_HOST")
    db_port = os.getenv("DB_PORT")
    DATABASE_URI = f"postgresql+asyncpg://{db_user}:{db_password}@{db_host}:" \
               f"{db_port}/{db_name}"

    jwt_access_secret_key = os.getenv("JWT_ACCESS_SECRET_KEY")
    jwt_refresh_secret_key = os.getenv("JWT_REFRESH_SECRET_KEY")


    algorithm = os.getenv("ALGORITHM")
    access_token_expire_minutes = os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES")
    refresh_token_expire_minutes = os.getenv("REFRESH_TOKEN_EXPIRE_MINUTES")


settings = Settings()
