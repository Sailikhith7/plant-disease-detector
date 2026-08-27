from fastapi import APIRouter

router = APIRouter(prefix="/api/cases", tags=["Cases"])

@router.get("/")
def list_cases():
    return {"status": "success", "cases": []}
