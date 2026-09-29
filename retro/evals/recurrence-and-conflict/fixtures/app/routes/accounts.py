from fastapi import APIRouter
from pydantic import BaseModel, ConfigDict
from pydantic.alias_generators import to_camel

from app.deps import DB
from app.repo import AccountRepo

router = APIRouter(prefix="/accounts")


class ExportOut(BaseModel):
    # PR #231: camelCase on the wire for new endpoints (priya); see the review thread.
    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)
    account_id: int
    exported_at: str | None


@router.get("/{account_id}/export", response_model=ExportOut, response_model_by_alias=True)
def export_account(account_id: int, db: DB):
    return AccountRepo(db).export(account_id)
