from fastapi import APIRouter

keys_router = APIRouter()

@keys_router.get("/")
async def get_keys():
    return {"keys": []}
