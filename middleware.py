from functools import wraps
import logging
from fastapi import HTTPException, Request, status
from jose import jwt, JWTError, ExpiredSignatureError
from datetime import datetime, timedelta, timezone

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configuration
SECRET_KEY = "5ef8bb3634321cc91db8fa5f037e7b83" 
ALGORITHM = "HS256"
TOKEN_EXPIRY = 60 


ROLE_ACCESS = {
    "doctor": ["doctor"],
    "nurse": ["nurse"],
    "management": ["management"]
}


def create_access_token(data: dict) -> str:
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(minutes=TOKEN_EXPIRY)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def require_auth(func):
    @wraps(func)
    async def wrapper(request: Request, *args, **kwargs):
        auth_header = request.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            raise HTTPException(status_code=401, detail="Missing or invalid token")
        
        token = auth_header.split(" ")[1]
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            request.state.user_id = payload.get("user_id")
            request.state.role = payload.get("role")
            logger.info(f"Auth successful - user_id: {request.state.user_id}, role: {request.state.role}")
        except JWTError as e:
            logger.error(f"JWT decode error: {e}")
            raise HTTPException(status_code=401, detail="Invalid or expired token")
        return await func(request, *args, **kwargs)
    return wrapper


def require_role(func):
    @wraps(func)
    async def wrapper(request: Request, *args, **kwargs):
        role = getattr(request.state, "role", None)
        if not role:
            raise HTTPException(status_code=401, detail="Role not found")

        endpoint = request.scope.get("route")
        tags = getattr(endpoint, "tags", False)

        if tags:
            authorized = any(role in ROLE_ACCESS.get(tag, []) for tag in tags)

            if not authorized:
                raise HTTPException(status_code=403, detail=f"Role '{role}' not authorized for this route")
                

        return await func(request, *args, **kwargs)
    return wrapper
