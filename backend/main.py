from pathlib import Path
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from backend.api.routes import router
from backend.auth.auth_routes import auth_router

app = FastAPI(title="GenAI Shopping Assistant API")

# Allow the frontend (opened as a local file or served on another port)
# to call this API during development.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router)
app.include_router(router)

frontend_dist = Path(__file__).resolve().parent.parent / "frontend" / "dist"
frontend_path = Path(__file__).resolve().parent.parent / "frontend"

if frontend_dist.exists():
    app.mount("/frontend", StaticFiles(directory=str(frontend_dist), html=True), name="frontend")
elif frontend_path.exists():
    app.mount("/frontend", StaticFiles(directory=str(frontend_path), html=True), name="frontend")


@app.get("/")
def health():
    return {
        "status": "ok",
        "message": "GenAI Shopping Assistant API is running",
        "docs": "/docs",
        "frontend": "/frontend/"
    }

