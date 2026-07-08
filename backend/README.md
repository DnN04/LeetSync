# LeetSync Pro Backend

FastAPI + SQLAlchemy + SQLite synchronization engine.

## Directory Layout
- `app/config/`: Configuration loaders and environment setting schemas.
- `app/core/`: Domain primitives.
- `app/services/`: Sync Engine, Statistics Engine, and scheduling logic.
- `app/integrations/`: GitHub and LeetCode GraphQL and Git integrations.
- `app/infrastructure/`: SQLite DB session managers and configurations.
- `app/models/`: Declarative schemas and Pydantic validation serialization schemas.
- `app/utilities/`: Custom structured JSON logging formatters.
- `tests/`: Automated unit testing suites.

## Local Launch

1. Install requirements:
   ```bash
   pip install -r requirements.txt
   ```
2. Set `.env` environment tokens.
3. Start backend locally:
   ```bash
   uvicorn app.main:app --reload
   ```
4. Run backend tests:
   ```bash
   $env:PYTHONPATH="backend"; python -m pytest tests/
   ```
