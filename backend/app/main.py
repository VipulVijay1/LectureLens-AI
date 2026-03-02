import os
from app.core.config import DATA_DIR
from fastapi import FastAPI
from app.routers import health
from app.routers import ingest
from app.routers import query
from app.core.model_loader import model_loader

app = FastAPI(title="LectureLens AI Backend")

# Include routers
app.include_router(health.router)
app.include_router(ingest.router)
app.include_router(query.router)

@app.on_event("startup")
def startup_event():
    os.makedirs(DATA_DIR, exist_ok=True)
    model_loader.load_models()
