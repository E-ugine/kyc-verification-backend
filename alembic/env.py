from logging.config import fileConfig
import os
from dotenv import load_dotenv
load_dotenv() 

from sqlalchemy import create_engine, pool
from alembic import context

# Import Base and models
from app.database import Base
from app import models  # ensures all models are registered

# Alembic Config object for .ini file values
config = context.config

# Set up Python logging if config file is present
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Add your metadata (used for autogenerating migrations)
target_metadata = Base.metadata

def get_database_url():
    """Get and validate database URL from environment."""
    url = os.getenv("DATABASE_URL")
    
    if not url:
        raise ValueError("DATABASE_URL environment variable is not set")
    
    # Convert postgres:// to postgresql:// for compatibility
    if url.startswith("postgres://"):
        url = url.replace("postgres://", "postgresql://", 1)
    
    # Ensure we have a driver specified
    if url.startswith("postgresql://") and "+" not in url:
        # Default to psycopg2 if no driver specified
        url = url.replace("postgresql://", "postgresql+psycopg2://", 1)
    
    print(f"Using database URL: {url.split('@')[0]}@[HIDDEN]")  # Log without credentials
    return url

def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode."""
    url = get_database_url()
    
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()

def run_migrations_online() -> None:
    """Run migrations in 'online' mode."""
    url = get_database_url()
    
    try:
        connectable = create_engine(url, poolclass=pool.NullPool)
    except Exception as e:
        print(f"Error creating engine: {e}")
        print("Make sure you have the appropriate database driver installed:")
        print("For PostgreSQL: pip install psycopg2-binary")
        print("For MySQL: pip install PyMySQL")
        print("For SQLite: No additional driver needed")
        raise

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            compare_type=True  # detects changes to column types
        )

        with context.begin_transaction():
            context.run_migrations()

# Choose online or offline mode
if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()