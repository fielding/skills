from typing import Annotated

from fastapi import Depends
from sqlalchemy.orm import Session

from app.db import get_db

# ruff B008 flags `Depends()` used as a default argument value. Wrapping the type in
# Annotated keeps the dependency declaration and satisfies the rule; we do not add B008
# to the ignore list.
DB = Annotated[Session, Depends(get_db)]
