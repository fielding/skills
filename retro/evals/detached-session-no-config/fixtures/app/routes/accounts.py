from fastapi import APIRouter

from app.deps import DB
from app.repo import AccountRepo

router = APIRouter(prefix="/accounts")


@router.get("/{account_id}/export")
def export_account(account_id: int, db: DB):
    return {"data": AccountRepo(db).export(account_id)}
