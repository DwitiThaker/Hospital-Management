# Authentication and Role-Based Access Control

## Security Overview

The system uses OAuth2 JWT bearer tokens for stateless authentication and bcrypt via `passlib` for password hashing. Role-based access control (RBAC) is enforced using Python decorators on route handlers.

## Password Hashing (`authentication.py`)

```python
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_pwd(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain_pwd: str, hashed_pwd: str) -> bool:
    return pwd_context.verify(plain_pwd, hashed_pwd)
```

## JWT Token Operations (`middleware.py`)

Tokens encode user identity (`user_id`, `role`) and an expiration timestamp:

```python
from jose import jwt
from datetime import datetime, timedelta, timezone

def create_access_token(data: dict) -> str:
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(minutes=TOKEN_EXPIRY)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
```

## Role-Based Access Control Decorators

Access policies map endpoints to roles (`doctor`, `nurse`, `management`):

```python
# Authorization Mapping
ROLE_ACCESS = {
    "doctor": ["doctor"],
    "nurse": ["nurse"],
    "management": ["management"],
}
```

### Decorator Pattern
- `@require_auth`: Extracts JWT from `Authorization` header, decodes payload, attaches `user_id` and `role` to `request.state`.
- `@require_role`: Checks `request.state.role` against endpoint tags. Raises HTTP 403 Forbidden if un-authorized.
