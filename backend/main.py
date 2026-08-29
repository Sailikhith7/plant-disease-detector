import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

# Routers
from backend.routers import analytics, cases, inputs, alerts, farmers

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

app = FastAPI(
    title="PikRakshak - Plant Disease Detection & Advisory API",
    description=(
        "AI-powered plant disease detection using MobileNetV3, "
        "RAG agronomic advisories, and regional outbreak dispatch."
    ),
    version="1.0.0",
)

# =========================================================
# CORS Setup (Allows Web Dashboard & Mobile App)
# =========================================================
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/uploads", StaticFiles(directory=UPLOAD_DIR), name="uploads")

# =========================================================
# Routers Mounting
# =========================================================
app.include_router(inputs.router, prefix="/api", tags=["Prediction & Inputs"])
app.include_router(cases.router, prefix="/api", tags=["Cases"])
app.include_router(analytics.router, prefix="/api", tags=["Analytics"])
app.include_router(alerts.router, prefix="/api/alerts", tags=["Alerts & Outbreaks"])
app.include_router(farmers.router)

# =========================================================
# Basic & Dashboard Endpoints
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
    return {"status": "healthy"}

@app.get("/dashboard")
def view_dashboard():
    if os.path.exists("static_dashboard.html"):
        return FileResponse("static_dashboard.html")
    return {"message": "Dashboard static asset not found. Use frontend web portal at http://localhost:5173"}