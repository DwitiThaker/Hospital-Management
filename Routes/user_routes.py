from fastapi import APIRouter, Depends, Request
from typing import Annotated
from jwt import ExpiredSignatureError

from authentication import *
from middleware import *
from Services.user_services import *
from MongoDB.schemas import Login, UserOut, UserCreate

user_auth_route = APIRouter()

def get_current_user(token: Annotated[str, Depends(oauth2_scheme)]):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id : str = payload.get("user_id")
        email: str = payload.get("email")
        user = get_user_by_email(email)

        return user

    except ExpiredSignatureError:
        logger.error(f"get_current_user: Token expired")
        raise HTTPException(status_code=401, detail="Token expired")
    
    except JWTError:
        logger.error(f"get_current_user: Token is invalid")
        raise HTTPException(status_code=401, detail="Invalid token")
    



@user_auth_route.post("/login")
def login(login_data: Login):
    try: 
        db_user = get_user_by_email(login_data.email)
        if not db_user:
            raise HTTPException(status_code=401, detail="Incorrect username or password")
        
        if not verify_password(login_data.password, db_user["password"]):
            raise HTTPException(status_code=401, detail="Incorrect username or password")
    
       
        logger.info(f"login: Creating Token....")

        token_data = {
            "email": db_user["email"],
            "user_id": str(db_user["_id"]), 
            "role": db_user["role"],
            "is_active": not db_user.get("disabled", False)                
        }

        access_token = create_access_token(token_data)  
    
        user_out = UserOut(
        username=db_user["username"],
        email=db_user["email"],
        is_active=db_user.get("is_active", True),
        role=db_user.get("role")
        )

        logger.info(f"login: User '{login_data.email}' logged in successfully")
        return {"user": user_out, "access_token": access_token, "token_type": "bearer"}
    
    except Exception as e:
        logger.error(f"login: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")



@user_auth_route.post("/register", response_model=UserOut)
@require_role
def register(user: UserCreate, request: Request):

    try:
        existing_user = get_user_by_email(user.email)
        if existing_user:
            logger.exception(f"register: email already exists")
            raise HTTPException(status_code=409, detail="email already exists")
        
        try:
            logger.info(f"register: hashing the password.......")
            hashed_pw = hash_pwd(user.password)
        except ValueError as val_err:
            logger.exception(f"register: Password hashing failed: {val_err}")
            raise HTTPException(status_code=500, detail="Password hashing failed")
        
        new_user = Users(
            username=user.username,
            password=hashed_pw,
            email=user.email, 
            is_active=True
        )

        try:
            logger.info(f"Register: Creating user...")
            created_user = create_user(new_user)

            if created_user:
                logging.info("User Created Successfully...")

                return UserOut(
                    username=created_user['username'],
                    email=created_user['email'],
                    is_active=created_user['is_active'],
                    role=created_user("role")
                )

        except Exception as db_err:
            logger.exception(f"register: Failed to create user {user.username}: {db_err}")
            raise HTTPException(status_code=500, detail="Failed to create user")
        
    except Exception as e: 
        logger.exception(f"Unexpected error during registration: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")
    

