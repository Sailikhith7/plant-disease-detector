import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse

from backend.routers import analytics, cases, inputs, alerts


app = FastAPI(
    title="PikRakshak - Plant Disease Detection & Advisory API",
    description=(
        "AI-powered plant disease detection using MobileNetV3, "
        "RAG agronomic advisories, and regional outbreak dispatch."
    ),
    version="1.0.0",
)


# =========================================================
# CORS
# =========================================================

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# =========================================================
# ROUTERS
#
# Router files already contain their own prefixes.
# Do NOT add another prefix here.
# =========================================================

app.include_router(inputs.router)
app.include_router(cases.router)
app.include_router(analytics.router)
app.include_router(alerts.router)


# =========================================================
# BASIC ENDPOINTS
# =========================================================

@app.get("/")
def root():
    return {
        "status": "online",
        "message": "Plant Disease Detection API is running.",
        "dashboard_url": "http://127.0.0.1:8000/dashboard",
    }


@app.get("/health")
def health():
    return {
        "status": "healthy"
    }


@app.get("/dashboard")
def view_dashboard():

    if os.path.exists("static_dashboard.html"):
        return FileResponse("static_dashboard.html")

    return {
        "message": (
            "Dashboard static asset not found. "
            "Use frontend web portal at "
            "http://localhost:5173"
        )
    }