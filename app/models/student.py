from pydantic import BaseModel, Field
from typing import Optional

class Student(BaseModel):
    student_id: str
    name: str
    age: int
    grade: str
    email: str
    gpa: float

class StudentUpdateRequest(BaseModel):
    name: Optional[str] = None
    age: Optional[int] = None
    grade: Optional[str] = None
    email: Optional[str] = None
    gpa: Optional[float] = None