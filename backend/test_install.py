"""Check required imports; exits nonzero if any dependency is missing."""
import importlib

if __name__ == "__main__":
    for name in ["fastapi", "sqlalchemy", "pdfplumber", "pydantic_settings", "jose", "bcrypt", "email_validator", "psycopg2"]:
        importlib.import_module(name)
        print(f"{name}: OK")
    print("Run python check_model.py to check the embedding model separately.")
