"""Quick test to verify installations"""
import sys

print("Testing installations...\n")

# Test basic packages
try:
    import fastapi
    print(f"✓ FastAPI {fastapi.__version__}")
except ImportError as e:
    print(f"✗ FastAPI: {e}")

try:
    import sqlalchemy
    print(f"✓ SQLAlchemy {sqlalchemy.__version__}")
except ImportError as e:
    print(f"✗ SQLAlchemy: {e}")

try:
    import pdfplumber
    print(f"✓ pdfplumber installed")
except ImportError as e:
    print(f"✗ pdfplumber: {e}")

try:
    import pydantic
    print(f"✓ Pydantic {pydantic.__version__}")
except ImportError as e:
    print(f"✗ Pydantic: {e}")

# Test AI packages
try:
    import sentence_transformers
    print(f"✓ sentence-transformers {sentence_transformers.__version__}")
except ImportError as e:
    print(f"✗ sentence-transformers: {e}")

try:
    import sklearn
    print(f"✓ scikit-learn {sklearn.__version__}")
except ImportError as e:
    print(f"✗ scikit-learn: {e}")

try:
    import spacy
    print(f"✓ spaCy {spacy.__version__}")
except ImportError as e:
    print(f"✗ spaCy: {e}")

print("\nPython version:", sys.version)
