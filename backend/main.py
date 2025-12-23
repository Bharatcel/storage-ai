from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routes import project_routes, question_routes, file_routes, script_routes, result_upload_routes, analysis_routes

app = FastAPI(title="Assessment App API", version="1.0.0")

# CORS middleware configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # React dev server
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def startup_event():
    """Initialize database tables on startup"""
    try:
        from app.database import engine, Base
        Base.metadata.create_all(bind=engine)
        print("✅ Database tables created successfully")
    except Exception as e:
        print(f"⚠️  Warning: Could not connect to database: {e}")
        print("💡 The API will run, but database operations will fail until you configure the database connection.")

# Include routers
app.include_router(project_routes.router, prefix="/api", tags=["Projects"])
app.include_router(question_routes.router, prefix="/api", tags=["Questions"])
app.include_router(file_routes.router, prefix="/api/files", tags=["File Upload"])
app.include_router(script_routes.router, prefix="/api/script", tags=["Script Download"])
app.include_router(result_upload_routes.router, prefix="/api/results", tags=["Script Results"])
app.include_router(analysis_routes.router, prefix="/api/analysis", tags=["Storage Analysis"])

@app.get("/")
def read_root():
    return {"message": "Assessment App API is running"}

@app.get("/health")
def health_check():
    return {"status": "healthy"}
