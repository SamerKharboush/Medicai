from typing import Optional, List
from pydantic import BaseModel, EmailStr, Field, validator
from datetime import date
from app.models.doctor import DoctorType, Specialty

class DoctorBase(BaseModel):
    email: EmailStr
    first_name: str = Field(min_length=2, max_length=50)
    last_name: str = Field(min_length=2, max_length=50)
    medical_license_number: str = Field(min_length=5, max_length=50)
    qualifications: str = Field(min_length=2, max_length=200)
    specialty: Specialty
    subspecialty: Optional[str] = None
    years_of_experience: int
    doctor_type: DoctorType
    date_of_birth: date
    gender: str = Field(pattern='^(male|female|other)$')
    contact_number: str = Field(pattern='^\+?[0-9]{10,20}$')
    emergency_contact: Optional[str] = None
    department: str
    office_location: Optional[str] = None
    consultation_hours: Optional[str] = None
    bio: Optional[str] = None
    research_interests: Optional[str] = None
    publications: Optional[str] = None
    certifications: Optional[str] = None

    @validator('years_of_experience')
    def validate_experience(cls, v):
        if v < 0:
            raise ValueError('Years of experience cannot be negative')
        return v

    @validator('date_of_birth')
    def validate_birth_date(cls, v):
        if v > date.today():
            raise ValueError('Birth date cannot be in the future')
        return v

class DoctorCreate(DoctorBase):
    password: str = Field(min_length=8)
    
    # Additional fields for residents
    supervisor_id: Optional[int] = None
    graduation_date: Optional[date] = None
    rotation_schedule: Optional[str] = None
    
    # Additional fields for consultants
    teaching_responsibilities: Optional[str] = None
    administrative_roles: Optional[str] = None

    @validator('password')
    def validate_password(cls, v):
        if not any(c.isupper() for c in v):
            raise ValueError('Password must contain at least one uppercase letter')
        if not any(c.islower() for c in v):
            raise ValueError('Password must contain at least one lowercase letter')
        if not any(c.isdigit() for c in v):
            raise ValueError('Password must contain at least one number')
        return v
    
    @validator('graduation_date')
    def validate_graduation_date(cls, v, values):
        if values.get('doctor_type') == DoctorType.RESIDENT and not v:
            raise ValueError('Graduation date is required for residents')
        if v and v < date.today():
            raise ValueError('Graduation date must be in the future')
        return v
    
    @validator('supervisor_id')
    def validate_supervisor(cls, v, values):
        if values.get('doctor_type') == DoctorType.RESIDENT and not v:
            raise ValueError('Supervisor ID is required for residents')
        return v

class DoctorUpdate(BaseModel):
    email: Optional[EmailStr] = None
    first_name: Optional[str] = Field(None, min_length=2, max_length=50)
    last_name: Optional[str] = Field(None, min_length=2, max_length=50)
    qualifications: Optional[str] = Field(None, min_length=2, max_length=200)
    specialty: Optional[Specialty] = None
    subspecialty: Optional[str] = None
    contact_number: Optional[str] = Field(None, pattern='^\+?[0-9]{10,20}$')
    emergency_contact: Optional[str] = None
    department: Optional[str] = None
    office_location: Optional[str] = None
    consultation_hours: Optional[str] = None
    bio: Optional[str] = None
    research_interests: Optional[str] = None
    publications: Optional[str] = None
    certifications: Optional[str] = None
    is_active: Optional[bool] = None
    rotation_schedule: Optional[str] = None
    graduation_date: Optional[date] = None
    teaching_responsibilities: Optional[str] = None
    administrative_roles: Optional[str] = None

class DoctorInDB(DoctorBase):
    id: int
    join_date: date
    is_active: bool
    supervisor_id: Optional[int] = None

    class Config:
        from_attributes = True

class Doctor(DoctorInDB):
    pass

class DoctorProfile(BaseModel):
    age: int
    full_name: str
    is_consultant: bool
    is_resident: bool
    supervised_residents: Optional[List['DoctorProfile']] = None

    class Config:
        from_attributes = True

# This is needed for the self-referential relationship
DoctorProfile.update_forward_refs()
