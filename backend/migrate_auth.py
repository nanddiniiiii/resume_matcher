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
        "UPDATE users SET password_hash = '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMesJU3QBnITJjKbWJqxHWKcfa' WHERE password_hash = ''"
    ]
    
    with engine.connect() as connection:
        for sql in migrations:
            try:
                connection.execute(text(sql))
                connection.commit()
                print(f"✓ Executed: {sql[:60]}...")
            except Exception as e:
                print(f"✗ Error: {e}")
    
    print("\n✓ Migration complete!")
    print("Note: Existing users have default password 'password123'")

if __name__ == "__main__":
    run_migration()
