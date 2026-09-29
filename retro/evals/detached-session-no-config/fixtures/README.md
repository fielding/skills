# ledgerd

Account ledger service. FastAPI + SQLAlchemy + alembic. Managed with uv.

    uv sync
    uv run pytest
    uv run ruff check .
    uv run alembic upgrade head
