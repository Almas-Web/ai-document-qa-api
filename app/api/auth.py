from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.dependencies import get_db
from app.models.user import User
from app.schemas.auth import (
    RegisterRequest,
    LoginRequest,
    TokenResponse,
)
from app.core.security import (
    hash_password,
    verify_password,
    create_access_token,
)

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/register", response_model=TokenResponse)
def register(
    request: RegisterRequest,
    db: Session = Depends(get_db),
):
    existing_user = (
        db.query(User)
        .filter(User.email == request.email)
        .first()
    )

    if existing_user:
        raise HTTPException(
            status_code=400,
            detail="Email already registered.",
        )

    user = User(
        email=request.email,
        hashed_password=hash_password(request.password),
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    access_token = create_access_token(
        data={"sub": str(user.id)}
    )

    return {
        "access_token": access_token,
        "token_type": "bearer",
    }


@router.post("/login", response_model=TokenResponse)
def login(
    request: LoginRequest,
    db: Session = Depends(get_db),
):
    user = (
        db.query(User)
        .filter(User.email == request.email)
        .first()
    )

    if not user or not verify_password(
        request.password,
        user.hashed_password,
    ):
        raise HTTPException(
            status_code=401,
            detail="Invalid email or password.",
        )

    access_token = create_access_token(
        data={"sub": str(user.id)}
    )

    return {
        "access_token": access_token,
        "token_type": "bearer",
    }