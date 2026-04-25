from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    PROJECT_NAME: str = "Taggy-Green API"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"
    
    # Database
    DATABASE_URL: str = "sqlite:///./taggy_green.db"
    
    model_config = SettingsConfigDict(env_file=".env", case_sensitive=True)

settings = Settings()
