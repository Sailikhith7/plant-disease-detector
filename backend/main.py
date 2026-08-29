import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

# Routers
from backend.routers import analytics, cases, inputs, alerts, farmers
try:
    from backend.routers import voice
    voice_router_available = True
except ImportError:
    voice_router_available = False

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

# Static directory for generated audio/TTS files
STATIC_DIR = os.path.join(os.path.dirname(__file__), "static")
os.makedirs(STATIC_DIR, exist_ok=True)
os.makedirs(os.path.join(STATIC_DIR, "audio"), exist_ok=True)

app = FastAPI(
    title="PikRakshak - Plant Disease Detection & Advisory API",
    description=(
        "AI-powered plant disease detection using MobileNetV3, "
        "RAG agronomic advisories, and regional voice outbreak dispatch."
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

# =========================================================
# Static Mounts
# =========================================================
app.mount("/uploads", StaticFiles(directory=UPLOAD_DIR), name="uploads")
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

# =========================================================
# Routers Mounting
# =========================================================
app.include_router(inputs.router, prefix="/api", tags=["Prediction & Inputs"])
app.include_router(cases.router, prefix="/api", tags=["Cases"])
app.include_router(analytics.router, prefix="/api", tags=["Analytics"])
app.include_router(alerts.router, prefix="/api/alerts", tags=["Alerts & Outbreaks"])
app.include_router(farmers.router)

if voice_router_available:
    app.include_router(voice.router, prefix="/api/voice", tags=["Voice Advisory"])

# =========================================================
# Basic & Dashboard Endpoints
# =========================================================
@app.get("/")
def root():
    return {
        "status": "online",
        "service": "PikRakshak API",
        "message": "Plant Disease Detection API is running.",
        "dashboard_url": "http://127.0.0.1:8000/dashboard",
        "docs_url": "http://127.0.0.1:8000/docs",
    }

@app.get("/health")
def health():
    return {"status": "healthy"}

@app.get("/dashboard")
def view_dashboard():
    if os.path.exists("static_dashboard.html"):
        return FileResponse("static_dashboard.html")
    return {"message": "Dashboard static asset not found. Use frontend web portal at http://localhost:5173"}