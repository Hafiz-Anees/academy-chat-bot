from fastapi import APIRouter

router = APIRouter(tags=["Health"])

@router.get("/health")
@router.head("/health")
def health():
    return {"status": "ok"}