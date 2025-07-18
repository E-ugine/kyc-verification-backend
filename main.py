from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse
from app.database import engine
from app import models
from app.routes import kyc, admin
import uvicorn
import os

# Create database tables
models.Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="KYC Verification Platform",
    description="Backend API for Know Your Customer verification",
    version="1.0.0"
)

# CORS middleware - More comprehensive configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:8080", 
        "http://localhost:5173", 
        "https://kyc-verification-frontend.vercel.app"
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "HEAD", "PATCH"],
    allow_headers=[
        "Accept",
        "Accept-Language",
        "Content-Language",
        "Content-Type",
        "Authorization",
        "X-Requested-With",
        "Origin",
        "Access-Control-Request-Method",
        "Access-Control-Request-Headers",
    ],
    expose_headers=["*"],
)

# Manual OPTIONS handler for additional safety
@app.options("/{path:path}")
async def options_handler(path: str):
    return JSONResponse(
        content={},
        headers={
            "Access-Control-Allow-Origin": "https://kyc-verification-frontend.vercel.app",
            "Access-Control-Allow-Methods": "GET, POST, PUT, DELETE, OPTIONS, HEAD, PATCH",
            "Access-Control-Allow-Headers": "Accept, Accept-Language, Content-Language, Content-Type, Authorization, X-Requested-With, Origin, Access-Control-Request-Method, Access-Control-Request-Headers",
            "Access-Control-Allow-Credentials": "true",
        }
    )

# Serve static files (uploaded documents)
app.mount("/media", StaticFiles(directory="media"), name="media")

# Include routers
app.include_router(kyc.router)
app.include_router(admin.router)

@app.get("/")
def root():
    return {"message": "KYC Verification Platform API", "docs": "/docs"}

@app.get("/health")
def health_check():
    return {"status": "healthy"}

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(
        "main:app",  
        host="0.0.0.0",
        port=port,
        reload=False
    )