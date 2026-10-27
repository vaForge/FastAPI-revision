from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict
from sqlalchemy.engine import URL 

class Settings(BaseSettings):
    # REad these from existing .env file used by docker compose
    #aliases march common postgresql env variable names
    postgres_user : str = Field(validation_alias="POSTGRES_USER")
    postgres_password: str = Field(validation_alias="POSTGRES_PASSWORD")
    postgres_db : str = Field(validation_alias="POSTGRES_DB")

    # app runs on host, outside docker
    db_host : str = Field(default="localhost",validation_alias="DB_HOST")
    db_port : int = Field(default=5432, validation_alias="DB_PORT")

    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore"
    )

    @property
    def database_url(self)->URL:
        return URL.create(
            drivername="postgresql+psycopg",
            username=self.postgres_user,
            password=self.postgres_password,
            host=self.db_host,
            port=self.db_port,
            database=self.postgres_db
        )

#One settings object shaerd by app
settings = Settings()


#Basesetttings loads values from env variables from .env files then validates their types 
#i.e. db_port = 5432 becomes int rather string

#using URL.create() rather than manually concantenatiion - handles safety automatically

