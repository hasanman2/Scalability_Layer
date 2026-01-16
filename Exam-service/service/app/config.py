from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    app_name: str = "Scalability Service"
    lms_db_url: str = "postgresql+psycopg://moodle:moodlepass@localhost:5433/moodle"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
