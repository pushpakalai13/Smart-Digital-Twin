from datetime import datetime, timezone
from fastapi import APIRouter, HTTPException, status, Depends
from app.db import get_db
from app.models.schemas import LoginRequest, RegisterRequest, TokenResponse
from app.core.security import verify_password, hash_password, create_access_token, get_current_user

router = APIRouter(prefix="/auth", tags=["Auth"])

@router.post("/register", response_model=TokenResponse)
def register_user(req: RegisterRequest):
    db = get_db()
    if db is None:
        raise HTTPException(status_code=500, detail="Database connection unavailable")

    existing = db.users.find_one({"email": req.email})
    if existing:
        raise HTTPException(status_code=400, detail="User with this email already exists")

    hashed_pwd = hash_password(req.password)
    user_doc = {
        "email": req.email,
        "password_hash": hashed_pwd,
        "name": req.name,
        "role": req.role if req.role in ["admin", "staff"] else "staff",
        "created_at": datetime.now(timezone.utc).isoformat()
    }
    res = db.users.insert_one(user_doc)
    
    token = create_access_token({"sub": req.email, "role": user_doc["role"], "name": req.name})
    return {
        "access_token": token,
        "token_type": "bearer",
        "user": {
            "id": str(res.inserted_id),
            "email": req.email,
            "name": req.name,
            "role": user_doc["role"]
        }
    }

@router.post("/login", response_model=TokenResponse)
def login_user(req: LoginRequest):
    db = get_db()
    if db is None:
        raise HTTPException(status_code=500, detail="Database connection unavailable")

    user = db.users.find_one({"email": req.email})
    if not user or not verify_password(req.password, user.get("password_hash", "")):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email or password")

    token = create_access_token({"sub": user["email"], "role": user.get("role", "staff"), "name": user.get("name", "")})
    return {
        "access_token": token,
        "token_type": "bearer",
        "user": {
            "id": str(user["_id"]),
            "email": user["email"],
            "name": user.get("name", "User"),
            "role": user.get("role", "staff")
        }
    }

@router.get("/me")
def get_me(current_user: dict = Depends(get_current_user)):
    return current_user
