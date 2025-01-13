from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.api.deps import get_db, get_current_doctor
from app.crud import doctor as crud_doctor
from app.models.doctor import Doctor, DoctorType
from app.schemas.doctor import (
    Doctor as DoctorSchema,
    DoctorCreate,
    DoctorUpdate
)

router = APIRouter()

@router.post("/", response_model=DoctorSchema)
def create_doctor(
    *,
    db: Session = Depends(get_db),
    doctor_in: DoctorCreate,
    current_doctor: Doctor = Depends(get_current_doctor)
) -> Doctor:
    """
    Create new doctor.
    Only consultants can create new doctors.
    """
    if current_doctor.doctor_type != DoctorType.CONSULTANT:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only consultants can create new doctors"
        )
    
    doctor = crud_doctor.get_doctor_by_email(db, email=doctor_in.email)
    if doctor:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Doctor with this email already exists"
        )
    return crud_doctor.create_doctor(db=db, doctor=doctor_in)

@router.get("/me", response_model=DoctorSchema)
def read_doctor_me(
    current_doctor: Doctor = Depends(get_current_doctor)
) -> Doctor:
    """
    Get current doctor.
    """
    return current_doctor

@router.put("/me", response_model=DoctorSchema)
def update_doctor_me(
    *,
    db: Session = Depends(get_db),
    doctor_in: DoctorUpdate,
    current_doctor: Doctor = Depends(get_current_doctor)
) -> Doctor:
    """
    Update current doctor.
    """
    return crud_doctor.update_doctor(db=db, db_doctor=current_doctor, doctor=doctor_in)

@router.get("/consultants", response_model=List[DoctorSchema])
def read_consultants(
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
    current_doctor: Doctor = Depends(get_current_doctor)
) -> List[Doctor]:
    """
    Retrieve consultants.
    """
    doctors = crud_doctor.get_doctors(
        db, skip=skip, limit=limit, doctor_type=DoctorType.CONSULTANT
    )
    return doctors

@router.get("/residents", response_model=List[DoctorSchema])
def read_residents(
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
    current_doctor: Doctor = Depends(get_current_doctor)
) -> List[Doctor]:
    """
    Retrieve residents.
    """
    doctors = crud_doctor.get_doctors(
        db, skip=skip, limit=limit, doctor_type=DoctorType.RESIDENT
    )
    return doctors

@router.get("/{doctor_id}", response_model=DoctorSchema)
def read_doctor(
    *,
    db: Session = Depends(get_db),
    doctor_id: int,
    current_doctor: Doctor = Depends(get_current_doctor)
) -> Doctor:
    """
    Get doctor by ID.
    """
    doctor = crud_doctor.get_doctor(db=db, doctor_id=doctor_id)
    if not doctor:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Doctor not found"
        )
    return doctor

@router.put("/{doctor_id}", response_model=DoctorSchema)
def update_doctor(
    *,
    db: Session = Depends(get_db),
    doctor_id: int,
    doctor_in: DoctorUpdate,
    current_doctor: Doctor = Depends(get_current_doctor)
) -> Doctor:
    """
    Update a doctor.
    Only consultants can update other doctors.
    """
    if current_doctor.doctor_type != DoctorType.CONSULTANT:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only consultants can update doctors"
        )
    
    doctor = crud_doctor.get_doctor(db=db, doctor_id=doctor_id)
    if not doctor:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Doctor not found"
        )
    return crud_doctor.update_doctor(db=db, db_doctor=doctor, doctor=doctor_in)
