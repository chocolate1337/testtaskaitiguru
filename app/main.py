import time
from fastapi import FastAPI
from app.api.v1 import api
from app.models.base import Base
from app.core.db import engine
from contextlib import asynccontextmanager

app = FastAPI(title="test task")

@asynccontextmanager
async def lifespan(app: FastAPI):
    # просто для теста, не стал алембик подрубать
    async with engine.begin() as conn:

        await conn.run_sync(Base.metadata.create_all)
    
    yield  
    
    await engine.dispose()

app = FastAPI(title="test task", lifespan=lifespan)

app.include_router(api.router)
