from fastapi import APIRouter, HTTPException, Depends, status
from typing import List
from app.models.student import Student, StudentUpdateRequest
from app.dependencies import get_current_user, require_admin
from app.database import get_db

router = APIRouter()

SEED_STUDENTS = [
    {
        "student_id": "S001",
        "name": "Aarav Sharma",
        "age": 20,
        "grade": "A",
        "email": "aarav.sharma@college.edu",
        "gpa": 3.9,
    },
    {
        "student_id": "S002",
        "name": "Priya Mehta",
        "age": 21,
        "grade": "B+",
        "email": "priya.mehta@college.edu",
        "gpa": 3.5,
    },
    {
        "student_id": "S003",
        "name": "Rohan Verma",
        "age": 19,
        "grade": "A-",
        "email": "rohan.verma@college.edu",
        "gpa": 3.7,
    },
]


async def ensure_seed():
    db = get_db()
    count = await db["students"].count_documents({})
    if count == 0:
        await db["students"].insert_many(SEED_STUDENTS)


@router.get("/", response_model=List[Student])
async def get_students(current_user: dict = Depends(get_current_user)):
    """Get all students """
    await ensure_seed()
    db = get_db()
    students = await db["students"].find({}, {"_id": 0}).to_list(100)
    return students


@router.get("/{student_id}", response_model=Student)
async def get_student(student_id: str, current_user: dict = Depends(get_current_user)):
    """Get a student by ID """
    db = get_db()
    student = await db["students"].find_one({"student_id": student_id}, {"_id": 0})
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    return student


@router.put("/{student_id}", response_model=Student)
async def update_student(
    student_id: str,
    body: StudentUpdateRequest,
    admin: dict = Depends(require_admin),
):
    """Update a student's information (admin only) """
    db = get_db()
    updates = {k: v for k, v in body.model_dump().items() if v is not None}
    if not updates:
        raise HTTPException(status_code=400, detail="No fields to update")

    result = await db["students"].find_one_and_update(
        {"student_id": student_id},
        {"$set": updates},
        return_document=True,
    )
    if not result:
        raise HTTPException(status_code=404, detail="Student not found")

    result.pop("_id", None)
    return result