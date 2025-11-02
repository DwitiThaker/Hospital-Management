from fastapi.security import OAuth2PasswordBearer
from passlib.context import CryptContext


pwd_context = CryptContext(schemes = ["bcrypt"],deprecated="auto")

def hash_pwd(password: str):
    return pwd_context.hash(password)

def verify_password(plain_pwd, hash_pwd):
    return pwd_context.verify(plain_pwd, hash_pwd)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl= "/login")



