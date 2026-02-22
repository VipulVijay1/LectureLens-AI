from fastapi import FastAPI
from app.routers import health
from app.routers import ingest
from app.core.model_loader import model_loader

app = FastAPI(title="LectureLens AI Backend")

# Include routers
app.include_router(health.router)
app.include_router(ingest.router)

@app.on_event("startup")
def startup_event():
    model_loader.load_models()
