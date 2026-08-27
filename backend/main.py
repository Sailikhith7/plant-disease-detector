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
    allow_methods=["*"],
    allow_headers=["*"],
)


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