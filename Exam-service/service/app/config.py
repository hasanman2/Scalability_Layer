from pydantic import BaseSettings 

class Settings(BaseSettings):
    app_name : str = "Scalability Service"
    lms_db_url : str = "mysql+pymysql://moodle:moodle@db/moodle"

    class Config:
        env_file = ".env"


settings = Settings()