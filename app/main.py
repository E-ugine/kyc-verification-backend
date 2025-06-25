from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from .database import engine
from . import models
from .routes import kyc, admin

# Create database tables
models.Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="KYC Verification Platform",
    description="Backend API for Know Your Customer verification",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8080", "http://localhost:5173"],  # React dev servers
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
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