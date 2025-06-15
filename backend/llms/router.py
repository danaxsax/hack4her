from fastapi import APIRouter

chat_router = APIRouter()

@chat_router.get("/health")
async def health_check():
    return {"status": "ok", "service": "chat"}
