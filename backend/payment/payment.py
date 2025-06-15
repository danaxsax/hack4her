from fastapi import APIRouter

buy_router = APIRouter()

@buy_router.get("/")
async def get_credits():
    return {"credits": 0}
