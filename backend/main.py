<<<<<<< HEAD
﻿from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from backend.routers import analytics, cases, inputs, alerts

app = FastAPI(title="PeekRakshak Advisory API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
=======
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.routers.inputs import router as inputs_router


app = FastAPI(
    title="Plant Disease Detection API",
    description=(
        "AI-powered plant disease detection "
        "using MobileNetV3, RAG and Ollama Cloud."
    ),
    version="1.0.0"
)


# =========================================================
# CORS
# =========================================================

app.add_middleware(
    CORSMiddleware,

    # Development: allow frontend applications to connect
    allow_origins=["*"],

    allow_credentials=False,
>>>>>>> d76ade7149b19c7dbaafb52db29ae82fccee1b39
    allow_methods=["*"],
    allow_headers=["*"],
)

<<<<<<< HEAD
app.include_router(cases.router)
app.include_router(analytics.router)
app.include_router(inputs.router)
app.include_router(alerts.router)

@app.get("/dashboard")
def view_dashboard():
    return FileResponse("static_dashboard.html")

@app.get("/")
def root():
    return {"status": "online", "dashboard_url": "http://127.0.0.1:8000/dashboard"}
=======

# =========================================================
# ROUTERS
# =========================================================

app.include_router(inputs_router)


# =========================================================
# BASIC ENDPOINTS
# =========================================================

@app.get("/")
def root():
    return {
        "message": "Plant Disease Detection API is running."
    }


@app.get("/health")
def health():
    return {
        "status": "healthy"
    }
>>>>>>> d76ade7149b19c7dbaafb52db29ae82fccee1b39
