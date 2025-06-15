import logging
import os

from fastapi import APIRouter, HTTPException, Depends
from fastapi.security import OAuth2PasswordBearer
from pydantic import BaseModel
from db.models.models import User
from db.schemas_chat.schemas import AuthResponse, UserProfile
from db.cruds.crud import get_user_by_email, create_user, update_access_token, get_user_by_token, create_stripe_user, get_stripe_user
from jose import jwt
from datetime import datetime, timedelta
from dotenv import load_dotenv
from bson.objectid import ObjectId

# Load environment variables from .env file
load_dotenv(override=True)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# TODO: Move these to a config file
SECRET_KEY = "2dagK4/1loucS2NJb1k07H8vVQL/D5bBdio0pJmYFWk="
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

auth_router = APIRouter()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/token")

class GoogleToken(BaseModel):
    token: str

async def  create_access_token(user_id: ObjectId, data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now() + expires_delta
    else:
        expire = datetime.now() + timedelta(minutes=30)

    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

    await update_access_token(user_id, encoded_jwt, expire)
    return encoded_jwt

@auth_router.post("/google", response_model=AuthResponse)
async def login_with_google(google_token: GoogleToken):
    try:
        # Verify the token
        print("STRIPE KEY FINAL:", os.getenv("STRIPE_SECRET_KEY"))

        idinfo = id_token.verify_oauth2_token(
            google_token.token, 
            requests.Request(), 
            "278205127983-fgjv1ctce8is40p6q9d83vqotltj908u.apps.googleusercontent.com",
            clock_skew_in_seconds=300)
        
        logger.info(f"Token verified: {idinfo}")

        if idinfo['iss'] not in ['accounts.google.com', 'https://accounts.google.com']:
            raise ValueError('Wrong issuer.')

        email = idinfo['email']
        name = idinfo.get('name', '')
        picture = idinfo.get('picture', '')
        user_name = idinfo.get('given_name', '')

        user = await get_user_by_email(email)
        print(f"User: {user}")
        if user is None:
            print(f"Creating new user")
            user = User(email=email, name=name, user_name=user_name, credits=250, picture=picture)
            await create_user(user)

        stripe_customer = await get_stripe_user(user.id)
        print(f"Stripe customer: {stripe_customer}")
        if stripe_customer is None:
            print(f"Creating new Stripe customer")
            stripe_customer = stripe.Customer.create( #crea nuevo cliente en stripe, mediante el se guardaran los metodos de pago
                email=email,
                name=name
            )

            print(f"Stripe customer created: {stripe_customer}")
            await create_stripe_user(stripe_customer, user.id)
            
        print(f"User2: {user}")
        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = await create_access_token(user.id, data={"sub": str(user.id)}, expires_delta=access_token_expires)
        user_profile = UserProfile(email=user.email, name=user.name, credits=user.credits, picture=user.picture)

        return AuthResponse(
            user=user_profile,
            access_token=access_token,
            token_type="bearer"
        )

    except ValueError as e:
        logger.error(f"Token validation error: {e}")
        raise HTTPException(status_code=400, detail="Invalid token")
    except Exception as e:
        logger.error(f"Error during Google login: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

async def verify_access_token(token: str = Depends(oauth2_scheme)):
    user = await get_user_by_token(token)

    if not user:
        print(f"Invalid access token")
        return {"error": True, "message": "Invalid access token", "status": 401}

    return {"error": False, "user": user, "status": 200}