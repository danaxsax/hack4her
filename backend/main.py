from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from llms.router import chat_router
from auth.auth import auth_router, verify_access_token
from api_keys.api_keys import keys_router
from payment.payment import buy_router


app = FastAPI(docs_url='/docs')

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(auth_router, prefix="/auth")
app.include_router(keys_router, prefix="/api-keys", dependencies=[Depends(verify_access_token)])
app.include_router(chat_router, prefix="/api", dependencies=[Depends(verify_access_token)])
app.include_router(buy_router, prefix="/credits")
