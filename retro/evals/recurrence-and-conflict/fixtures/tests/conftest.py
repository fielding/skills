import pytest
from sqlalchemy import create_engine


@pytest.fixture
def engine(tmp_path):
    # One sqlite FILE per test. Under pytest-xdist every worker is its own process, so an
    # in-memory ":memory:" database is never shared and fixtures that seed it silently
    # apply to a different connection. tmp_path gives each test its own file.
    return create_engine(f"sqlite:///{tmp_path / 'test.db'}")
