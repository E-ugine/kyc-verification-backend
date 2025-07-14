# KYC Verification Backend

This is the backend API for the KYC Verification Platform. Built with FastAPI and PostgreSQL, it handles document uploads, user verification, admin approval workflows, and secure JWT-based authentication.

---
## Tech Stack

- **FastAPI**   
- **Pydantic** – Elegant data validation & parsing  
- **SQLAlchemy**   
- **PostgreSQL** 
- **JWT**   
- **Alembic** – DB migrations  
- **Docker & Docker Compose** – Containerized development  
- **Uvicorn** – Lightweight ASGI server  

---

## Getting Started Locally with Docker

### Prerequisites

- [Docker](https://www.docker.com/products/docker-desktop)
- [Docker Compose](https://docs.docker.com/compose/)
- Git

---

###Clone & Boot the Stack

```bash
# 1. Clone the repository
git clone https://github.com/E-ugine/kyc-verification-backend.git
cd kyc-verification-backend

# 2. Create a .env file
```bash
cp .env.example .env

Update .env with your desired values. For example:

DATABASE_URL=postgresql://kyc_user:Strong1221!@db:5432/kyc_verify
SECRET_KEY=your-super-secret-key

 Run the app with Docker
```bash
docker-compose up --build

The backend will be live at: http://localhost:8000

PostgreSQL runs inside a container on port 5432

Apply Alembic Migrations
```bash
docker-compose exec backend alembic upgrade head

This applies all migration scripts to the containerized database.



 Running Locally (Without Docker)
If you prefer using your system's Python + PostgreSQL:

Prerequisites
Python 3.12

PostgreSQL installed and running

Setup Instructions
```bash
# Clone the repo
git clone https://github.com/E-ugine/kyc-verification-backend.git
cd kyc-verification-backend

# Create and activate a virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Create .env file
cp .env.example .env
PostgreSQL Setup (Manual)
Inside psql:

```sql
CREATE DATABASE kyc_verify;
CREATE USER your_user WITH PASSWORD 'your_password';
GRANT ALL PRIVILEGES ON DATABASE kyc_verify TO your_user;
Update .env accordingly:

```env
DATABASE_URL=postgresql://your_user:your_password@localhost:5432/kyc_verify


Run the API Server
```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000
Server will run on http://localhost:8000

 Alembic Migrations
```bash
alembic upgrade head

🌐API Docs
FastAPI auto-generates docs:

Swagger UI → http://localhost:8000/docs

ReDoc → http://localhost:8000/redoc

CI/CD & Deployment
This project supports GitHub Actions CI and automatic deploys to Render. Alembic migrations run during CI.

