# KYC Verification Backend

This is the backend API for the KYC Verification Platform. Built with FastAPI and PostgreSQL, it handles document uploads, user verification, admin approval flows, and secure authentication using JWT.

---

## Tech Stack

- **FastAPI** – High-performance Python web framework  
- **Pydantic** – Data validation and settings management  
- **SQLAlchemy** – ORM for database interactions  
- **PostgreSQL** – Relational database  
- **JWT** – Token-based authentication  
- **Uvicorn** – ASGI server for running FastAPI  

---

## Getting Started Locally

### Prerequisites

- Python 3.10+
- PostgreSQL installed and running
- Git

### Clone and Set Up Project

```bash
# 1. Clone the repository
git clone git@github.com:E-ugine/kyc-verification-backend.git
cd kyc-verification-backend

# 2. Create and activate virtual environment
python3 -m venv venv
source venv/bin/activate

# 3. Install dependencies
pip install -r requirements.txt


Setting Up Environment Variables & Database
# 1. Copy the example env file
cp .env.example .env
Open .env and configure the DATABASE_URL, SECRET_KEY, and other required values.

PostgreSQL Setup (optional sample)
-- Inside psql:
CREATE DATABASE kyc_verify;
CREATE USER your_user WITH PASSWORD 'your_password';
GRANT ALL PRIVILEGES ON DATABASE kyc_verify TO your_user;


▶️ Running the Server

uvicorn app.main:app --reload
App will run on http://localhost:8000.