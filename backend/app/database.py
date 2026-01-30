from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import QueuePool
from app.config import settings

# Create database engine with optimized connection pool
engine = create_engine(
    settings.database_url,
    echo=True if settings.ENVIRONMENT == "development" else False,
    
    # Connection Pool Configuration (PERFORMANCE OPTIMIZATION)
    poolclass=QueuePool,           # Use queue-based pool for thread safety
    pool_size=10,                   # Maintain 10 persistent connections (default: 5)
    max_overflow=20,                # Allow 20 additional connections during peak (total max: 30)
    pool_timeout=30,                # Wait 30s for connection before failing (default: 30)
    pool_recycle=3600,              # Recycle connections every hour (Azure SQL timeout = 30min)
    pool_pre_ping=True,             # Validate connections before use (catch stale connections)
    
    # Query Performance
    echo_pool=False,                # Don't log pool checkouts (reduces noise)
    
    # Connection arguments for Azure SQL
    connect_args={
        "connect_timeout": 30,      # Connection timeout in seconds
        "timeout": 30,              # Query timeout in seconds
    } if "mssql" in settings.database_url else {}
)

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create base class for models
Base = declarative_base()

# Dependency to get DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
