from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    DB_DRIVER: str = "ODBC Driver 18 for SQL Server"
    DB_SERVER: str
    DB_DATABASE: str
    DB_USERNAME: str
    DB_PASSWORD: str
    DB_PORT: int = 1433
    ENVIRONMENT: str = "development"
    
    # Azure Blob Storage
    AZURE_STORAGE_CONNECTION_STRING: str = ""
    AZURE_STORAGE_CONTAINER_NAME: str = "assessment-uploads"

    class Config:
        env_file = ".env"
        case_sensitive = True

    @property
    def database_url(self) -> str:
        return (
            f"mssql+pyodbc://{self.DB_USERNAME}:{self.DB_PASSWORD}@"
            f"{self.DB_SERVER}:{self.DB_PORT}/{self.DB_DATABASE}?"
            f"driver={self.DB_DRIVER.replace(' ', '+')}&"
            f"Encrypt=yes&TrustServerCertificate=no"
        )

settings = Settings()
