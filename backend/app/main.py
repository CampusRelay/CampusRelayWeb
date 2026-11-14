from fastapi import FastAPI

from app.routers import health

app = FastAPI(
    title="CampusRelay API",
    description="CampusRelay Backend Service",
    version="1.0.0",
)

app.include_router(health.router)


@app.get("/")
def root():
    return {
        "name": "CampusRelay",
        "message": "CampusRelay API is running",
    }
