"""
Database migration to add authentication fields to users table.
Run this ONCE after updating the User model.
"""
from sqlalchemy import text
from app.database import engine

def run_migration():
    """Run the migration."""
    print("Running database migration...")
    print("Adding authentication fields to users table...")

    migrations = [
        "ALTER TABLE users ADD COLUMN IF NOT EXISTS password_hash VARCHAR DEFAULT ''",
        "ALTER TABLE users ADD COLUMN IF NOT EXISTS is_active BOOLEAN DEFAULT TRUE",
        "UPDATE users SET is_active = FALSE WHERE password_hash IS NULL OR password_hash = '' OR password_hash = '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMesJU3QBnITJjKbWJqxHWKcfa'"
    ]

    with engine.begin() as connection:
        for sql in migrations:
            connection.execute(text(sql))
    print("Authentication migration applied")

    print("\n✓ Migration complete!")
    print("Note: Legacy accounts without password hashes are disabled; reset them through a trusted administrative process.")

if __name__ == "__main__":
    run_migration()
