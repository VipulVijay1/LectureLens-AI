from fastapi import FastAPI
from app.routers import health
from app.core.model_loader import model_loader

app = FastAPI(title="LectureLens AI Backend")

# Include routers
app.include_router(health.router)

@app.on_event("startup")
def startup_event():
    model_loader.load_models()
