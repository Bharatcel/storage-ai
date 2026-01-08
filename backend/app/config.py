from pydantic_settings import BaseSettings
from typing import Optional
import os

class Settings(BaseSettings):
    # Direct database URL (highest priority - use this if you have a full connection string)
    DATABASE_URL: Optional[str] = None
    
    # Individual database settings (fallback if DATABASE_URL not provided)
    DB_DRIVER: Optional[str] = None
    DB_SERVER: Optional[str] = None
    DB_DATABASE: Optional[str] = None
    DB_USERNAME: Optional[str] = None
    DB_PASSWORD: Optional[str] = None
    DB_PORT: int = 1433
    ENVIRONMENT: str = "development"
    
    # Azure AD Authentication (alternative to username/password)
    USE_AZURE_AD_AUTH: bool = False
    
    # Azure Blob Storage
    AZURE_STORAGE_CONNECTION_STRING: str = ""
    AZURE_STORAGE_CONTAINER_NAME: str = "assessment-uploads"

    class Config:
        env_file = ".env"
        case_sensitive = True

    @property
    def database_url(self) -> str:
        """Generate database URL based on authentication method"""
        
        # Option 1: Direct DATABASE_URL (highest priority)
        if self.DATABASE_URL:
            print(f"✅ Using DATABASE_URL connection string")
            return self.DATABASE_URL
        
        # Option 2: If no server/database, use local SQLite
        if not self.DB_SERVER or not self.DB_DATABASE:
            db_url = "sqlite:///./assessment.db"
            print(f"✅ Using SQLite database: {db_url}")
            return db_url
        
        # Option 3: Azure AD Authentication
        if self.USE_AZURE_AD_AUTH and self.DB_DRIVER:
            db_url = (
                f"mssql+pyodbc://@{self.DB_SERVER}:{self.DB_PORT}/{self.DB_DATABASE}?"
                f"driver={self.DB_DRIVER.replace(' ', '+')}&"
                f"Authentication=ActiveDirectoryInteractive&"
                f"Encrypt=yes&TrustServerCertificate=no"
            )
            print(f"✅ Using Azure AD authentication")
            return db_url
        
        # Option 4: SQL Authentication (username/password)
        if self.DB_USERNAME and self.DB_PASSWORD and self.DB_DRIVER:
            db_url = (
                f"mssql+pyodbc://{self.DB_USERNAME}:{self.DB_PASSWORD}@"
                f"{self.DB_SERVER}:{self.DB_PORT}/{self.DB_DATABASE}?"
                f"driver={self.DB_DRIVER.replace(' ', '+')}&"
                f"Encrypt=yes&TrustServerCertificate=no"
            )
            print(f"✅ Using SQL authentication")
            return db_url
        
        # Option 5: Fallback to SQLite
        db_url = "sqlite:///./assessment.db"
        print(f"✅ Falling back to SQLite database: {db_url}")
        return db_url

settings = Settings()
