"""CMFH Main Application
FastAPI backend for AI TEDX Speech Coach
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import uvicorn

from app.api import router, ws_router
from app.core.registry import registry


@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Starting CMFH - Call Me For Help...")
    print("AI TEDX Speech Coach initializing...")
    registry.warmup()
    yield
    print("CMFH shutting down...")


app = FastAPI(
    title="CMFH - Call Me For Help",
    description="AI TEDX Speech Coach & Professional Communication Assistant",
    version="1.0.0",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router, prefix="/api")
app.include_router(ws_router, prefix="/api")


@app.get("/")
async def root():
    return {
        "name": "CMFH - Call Me For Help",
        "subtitle": "AI TEDX Speech Coach & Professional Communication Assistant",
        "version": "1.0.0",
        "status": "running"
    }


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )