from fastapi import APIRouter

router = APIRouter(tags=["Health"])


@router.get("/health",methods=["GET", "HEAD"])
def health():
    return {"status": "ok"}