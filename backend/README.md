# Backend

FastAPI, SQLAlchemy and Sentence Transformers. See the [project README](../README.md#backend) for setup, configuration and model behavior.

Run `python main.py` from this directory. `python check_model.py` checks real model loading; `python init_db.py` creates the schema and loads demonstration jobs.

API documentation: `http://localhost:8000/docs`. Readiness: `/health`.

See [the audit](../docs/AUDIT.md) for regressions fixed and remaining limits.
