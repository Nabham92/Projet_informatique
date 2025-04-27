from fastapi import FastAPI
from backend.api.endpoints import router

app = FastAPI(
    title="Film Recommender API",
    version="1.0",
)

app.include_router(router)
