from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from backend.routers import analytics, cases, inputs, alerts

app = FastAPI(title="PeekRakshak Advisory API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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
