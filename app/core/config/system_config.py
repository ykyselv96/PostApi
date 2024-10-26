import dotenv
import os


class Settings:
    """Configuration settings for the application.

    This class loads environment variables using the `dotenv` library and
    initializes various settings used throughout the application, including
    database connection details and JWT configurations.

    Attributes:
        app_port (str): The port on which the application will run.
        app_host (str): The host address of the application.
        db_name (str): The name of the PostgreSQL database.
        db_user (str): The username for connecting to the PostgreSQL database.
        db_password (str): The password for connecting to the PostgreSQL database.
        db_host (str): The host address for the PostgreSQL database.
        db_port (str): The port number for connecting to the PostgreSQL database.
        DATABASE_URI (str): The database connection URI formatted for asyncpg.
        jwt_access_secret_key (str): The secret key used for signing JWT access tokens.
        jwt_refresh_secret_key (str): The secret key used for signing JWT refresh tokens.
        algorithm (str): The algorithm used for encoding the JWT tokens.
        access_token_expire_minutes (str): The expiration time for access tokens in minutes.
        refresh_token_expire_minutes (str): The expiration time for refresh tokens in minutes.
        google_cloud_project_id (str): The ID of the Google Cloud project.
    """

    dotenv.load_dotenv()

    app_port = os.getenv("PORT")
    app_host = os.getenv("HOST")
    db_name = os.getenv("POSTGRES_DB")
    db_user = os.getenv("POSTGRES_USER")
    db_password = os.getenv("POSTGRES_PASSWORD")
    db_host = os.getenv("POSTGRES_HOST")
    db_port = os.getenv("POSTGRES_PORT")
    DATABASE_URI = f"postgresql+asyncpg://{db_user}:{db_password}@{db_host}:" \
               f"{db_port}/{db_name}"

    jwt_access_secret_key = os.getenv("JWT_ACCESS_SECRET_KEY")
    jwt_refresh_secret_key = os.getenv("JWT_REFRESH_SECRET_KEY")

    algorithm = os.getenv("ALGORITHM")
    access_token_expire_minutes = os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES")
    refresh_token_expire_minutes = os.getenv("REFRESH_TOKEN_EXPIRE_MINUTES")
    google_cloud_project_id = os.getenv("GOOGLE_CLOUD_PROJECT_ID")

    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "charismatic-sum-439609-g7-230a4ff5cd79.json"

settings = Settings()
