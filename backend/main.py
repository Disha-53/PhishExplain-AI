from __future__ import annotations

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.api.routes_analyze import router as analyze_router
from backend.api.routes_health import router as health_router
from backend.config import API_HOST, API_PORT, cors_origins

app = FastAPI(title="PhishExplain AI", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins(),
    allow_origin_regex=r"^chrome-extension://[a-p]{32}$",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health_router)
app.include_router(analyze_router)


@app.get("/")
def root() -> dict:
    return {"message": "PhishExplain AI backend is running."}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("backend.main:app", host=API_HOST, port=API_PORT, reload=True)
