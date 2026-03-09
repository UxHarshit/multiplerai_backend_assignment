from fastapi import APIRouter, HTTPException, status
from app.models.user import SignupRequest, LoginRequest, TokenResponse, UserResponse
from app.utils.jwt import hash_password, verify_password, create_access_token
from app.database import get_db

router = APIRouter()


@router.post("/signup", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def signup(body: SignupRequest):
    """Register a new user. Pass 'admin' as role for admin users, otherwise 'user'."""
    db = get_db()

    if await db["users"].find_one({"email": body.email}):
        raise HTTPException(status_code=400, detail="Email already registered")
    
    if await db["users"].find_one({"username": body.username}):
        raise HTTPException(status_code=400, detail="Username already taken")

    try:
        hashed_password = hash_password(body.password)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    new_user = {
        "username": body.username,
        "email": body.email,
        "hashed_password": hashed_password,
        "role": body.role,
    }
    await db["users"].insert_one(new_user)

    return UserResponse(username=body.username, email=body.email, role=body.role)


@router.post("/login", response_model=TokenResponse)
async def login(body: LoginRequest):
    db = get_db()
    user = await db["users"].find_one({"email": body.email})

    if not user or not verify_password(body.password, user["hashed_password"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        )

    token = create_access_token(data={"sub": user["email"], "role": user["role"]})

    return TokenResponse(
        access_token=token,
        user=UserResponse(
            username=user["username"],
            email=user["email"],
            role=user["role"],
        ),
    )