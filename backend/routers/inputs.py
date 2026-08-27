from fastapi import APIRouter

router = APIRouter(prefix="/api/inputs", tags=["Inputs"])

@router.get("/")
def list_inputs():
    return {"status": "success", "inputs": []}
