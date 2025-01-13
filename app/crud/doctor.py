from typing import List, Optional
from sqlalchemy.orm import Session
from fastapi.encoders import jsonable_encoder
from app.core.security import get_password_hash
from app.models.doctor import Doctor, DoctorType
from app.schemas.doctor import DoctorCreate, DoctorUpdate
from datetime import date

def get_doctor(db: Session, doctor_id: int) -> Optional[Doctor]:
    return db.query(Doctor).filter(Doctor.id == doctor_id).first()

def get_doctor_by_email(db: Session, email: str) -> Optional[Doctor]:
    return db.query(Doctor).filter(Doctor.email == email).first()

def get_doctors(
    db: Session, 
    skip: int = 0, 
    limit: int = 100,
    doctor_type: Optional[DoctorType] = None
) -> List[Doctor]:
    query = db.query(Doctor)
    if doctor_type:
        query = query.filter(Doctor.doctor_type == doctor_type)
    return query.offset(skip).limit(limit).all()

def create_doctor(db: Session, doctor: DoctorCreate) -> Doctor:
    db_doctor = Doctor(
        email=doctor.email,
        hashed_password=get_password_hash(doctor.password),
        first_name=doctor.first_name,
        last_name=doctor.last_name,
        medical_license_number=doctor.medical_license_number,
        qualifications=doctor.qualifications,
        specialty=doctor.specialty,
        subspecialty=doctor.subspecialty,
        years_of_experience=doctor.years_of_experience,
        doctor_type=doctor.doctor_type,
        date_of_birth=doctor.date_of_birth,
        gender=doctor.gender,
        contact_number=doctor.contact_number,
        emergency_contact=doctor.emergency_contact,
        department=doctor.department,
        office_location=doctor.office_location,
        graduation_date=doctor.graduation_date if doctor.doctor_type == DoctorType.RESIDENT else None,
        supervisor_id=doctor.supervisor_id if doctor.doctor_type == DoctorType.RESIDENT else None,
        rotation_schedule=doctor.rotation_schedule if doctor.doctor_type == DoctorType.RESIDENT else None,
        teaching_responsibilities=doctor.teaching_responsibilities if doctor.doctor_type == DoctorType.CONSULTANT else None,
        administrative_roles=doctor.administrative_roles if doctor.doctor_type == DoctorType.CONSULTANT else None,
        join_date=date.today(),
        is_active=True
    )
    db.add(db_doctor)
    db.commit()
    db.refresh(db_doctor)
    return db_doctor

def update_doctor(
    db: Session, 
    db_doctor: Doctor,
    doctor: DoctorUpdate
) -> Doctor:
    obj_data = jsonable_encoder(db_doctor)
    update_data = doctor.model_dump(exclude_unset=True)
    
    if update_data.get("password"):
        update_data["hashed_password"] = get_password_hash(update_data.pop("password"))
    
    for field in obj_data:
        if field in update_data:
            setattr(db_doctor, field, update_data[field])
    
    db.add(db_doctor)
    db.commit()
    db.refresh(db_doctor)
    return db_doctor

def delete_doctor(db: Session, doctor_id: int) -> Optional[Doctor]:
    doctor = db.query(Doctor).filter(Doctor.id == doctor_id).first()
    if doctor:
        db.delete(doctor)
        db.commit()
    return doctor
