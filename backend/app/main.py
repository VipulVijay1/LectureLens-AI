import os
from app.core.config import DATA_DIR
from fastapi import FastAPI
from app.routers import health
from app.routers import ingest
from app.routers import query
from app.core.model_loader import model_loader
from fastapi.middleware.cors import CORSMiddleware
from app.routers import storage
from app.routers import flashcards
from app.routers import notes

app = FastAPI(title="LectureLens AI Backend")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # for development
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(health.router)
app.include_router(ingest.router)
app.include_router(query.router)
app.include_router(storage.router)
app.include_router(flashcards.router)
app.include_router(notes.router)


@app.on_event("startup")
def startup_event():
    os.makedirs(DATA_DIR, exist_ok=True)
    model_loader.load_models()
