from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routes import auth, screenshot, students
from app.database import connect_db, close_db
from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Starting up the server")
    await connect_db()
    yield
    print("Shutting down the server")
    await close_db()


app = FastAPI(title="Backend", version="1.0.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(auth.router, prefix="/auth", tags=["Auth"])
app.include_router(students.router, prefix="/students", tags=["Students"])
app.include_router(screenshot.router, prefix="/screenshot", tags=["Screenshot"])

@app.get("/")
async def root():
    return {"message": "Server is running"}