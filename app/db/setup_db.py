import subprocess
import sys
import os
import time
from sqlalchemy import text, inspect
from sqlalchemy.exc import OperationalError
from app.db.database import engine, SessionLocal
from app.db.test_data import create_test_data

def wait_for_db(max_retries=5, delay=2):
    """Wait for database to become available."""
    for attempt in range(max_retries):
        try:
            with engine.connect() as conn:
                conn.execute(text("SELECT 1"))
                return True
        except OperationalError:
            if attempt < max_retries - 1:
                print(f"Database not ready, waiting {delay} seconds... (attempt {attempt + 1}/{max_retries})")
                time.sleep(delay)
            continue
    return False

def check_alembic_version():
    """Check if alembic_version table exists and has any records."""
    try:
        inspector = inspect(engine)
        if 'alembic_version' in inspector.get_table_names():
            with engine.connect() as conn:
                result = conn.execute(text("SELECT version_num FROM alembic_version")).first()
                return bool(result)
    except Exception as e:
        print(f"Error checking alembic version: {e}", file=sys.stderr)
    return False

def run_alembic_command(command, env, check=True):
    """Run an alembic command with proper environment and error handling."""
    try:
        result = subprocess.run(
            command,
            env=env,
            check=check,
            capture_output=True,
            text=True
        )
        if result.stdout:
            print(result.stdout)
        if result.stderr:
            print(result.stderr, file=sys.stderr)
        return result
    except subprocess.CalledProcessError as e:
        print(f"Error running command {' '.join(command)}: {e}", file=sys.stderr)
        if e.stdout:
            print(f"stdout: {e.stdout}", file=sys.stderr)
        if e.stderr:
            print(f"stderr: {e.stderr}", file=sys.stderr)
        raise

def clean_database():
    """Drop all tables in the database."""
    with engine.connect() as conn:
        conn.execute(text("""
            DO $$ DECLARE
                r RECORD;
            BEGIN
                FOR r IN (SELECT tablename FROM pg_tables WHERE schemaname = current_schema()) LOOP
                    EXECUTE 'DROP TABLE IF EXISTS ' || quote_ident(r.tablename) || ' CASCADE';
                END LOOP;
            END $$;
        """))
        conn.commit()

def setup_db() -> None:
    try:
        print("Waiting for database to be ready...")
        if not wait_for_db():
            raise RuntimeError("Database not available after maximum retries")

        print("Checking database state...")
        inspector = inspect(engine)
        tables_exist = bool(inspector.get_table_names())
        has_migrations = check_alembic_version()

        # Set up environment for Alembic
        env = os.environ.copy()
        if not env.get("DATABASE_URL"):
            env["DATABASE_URL"] = "postgresql://postgres:postgres@db:5432/medicai"
        env["PYTHONPATH"] = "/app"

        if tables_exist:
            print("Cleaning existing database...")
            clean_database()
            tables_exist = False
            has_migrations = False

        print("Running fresh database setup...")
        # First, stamp the base to clear any existing migration state
        run_alembic_command(["alembic", "stamp", "base"], env, check=False)
        
        # Then run all migrations
        print("Running database migrations...")
        run_alembic_command(["alembic", "upgrade", "head"], env)
        
        print("Creating test data...")
        db = SessionLocal()
        try:
            create_test_data(db)
            db.commit()
            print("Test data created successfully!")
        except Exception as e:
            print(f"Error creating test data: {e}", file=sys.stderr)
            db.rollback()
            raise
        finally:
            db.close()
                
    except Exception as e:
        print(f"Unexpected error during database setup: {e}", file=sys.stderr)
        raise

if __name__ == "__main__":
    setup_db()
