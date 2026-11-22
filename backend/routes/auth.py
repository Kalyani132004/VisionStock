# routes/auth.py - login and registration


from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import User
from ..schemas import LoginIn, RegisterIn, TokenOut, UserOut
from ..security import check_password, create_token, get_current_user, hash_password

router = APIRouter(prefix="/api/auth", tags=["Auth"])


@router.post("/register", response_model=TokenOut, status_code=201)
def register(data: RegisterIn, db: Session = Depends(get_db)):
    # data.email is already cleaned (small letters) by the schema
    if db.query(User).filter(User.email == data.email).first() is not None:
        raise HTTPException(status_code=409, detail="An account with this email already exists")

    user = User(
        name=data.name,
        email=data.email,
        password_hash=hash_password(data.password),
        role="Staff",                      # always Staff, never taken from the request
    )
    db.add(user)
    try:
        db.commit()
    except IntegrityError:
        # two people registered the same email at the same moment
        db.rollback()
        raise HTTPException(status_code=409, detail="An account with this email already exists")
    db.refresh(user)

    return {"access_token": create_token(user), "token_type": "bearer", "user": user}


@router.post("/login", response_model=TokenOut)
def login(data: LoginIn, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == data.email.strip().lower()).first()

    # same message for "no such user" and "wrong password"
    if user is None or not check_password(data.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid email or password")

    return {"access_token": create_token(user), "token_type": "bearer", "user": user}


@router.get("/me", response_model=UserOut)
def me(user: User = Depends(get_current_user)):
    return user
