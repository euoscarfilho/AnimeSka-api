from fastapi import FastAPI
from app.routers import v1

app = FastAPI(title="Anime Scraper API", version="1.0.0")

app.include_router(v1.router, prefix="/api/v1")

@app.get("/")
async def root():
    return {"message": "Anime Scraper API is running"}
