from fastapi import FastAPI

from app.routes import accounts

app = FastAPI(title="ledgerd")
app.include_router(accounts.router)
