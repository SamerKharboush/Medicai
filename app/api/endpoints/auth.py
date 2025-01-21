from datetime import timedelta
from typing import Any, Dict
from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
import logging

from app.core.security import verify_password, create_access_token, get_password_hash
from app.core.config import get_settings
from app.api.deps import get_db, get_current_doctor
from app.crud import doctor as crud_doctor
from app.models.doctor import Doctor, DoctorType
from app.schemas.doctor import DoctorCreate, Doctor as DoctorSchema

router = APIRouter()
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG)

settings = get_settings()

@router.options("/token")
async def token_options():
    return JSONResponse(
        content={"message": "OK"},
        headers={
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "POST, OPTIONS",
            "Access-Control-Allow-Headers": "Content-Type, Authorization",
        },
    )

@router.post("/token")
async def login_for_access_token(
    request: Request,
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
) -> Dict[str, str]:
    logger.debug(f"Login attempt for doctor: {form_data.username}")
    logger.debug(f"Request headers: {dict(request.headers)}")
    logger.debug(f"Request method: {request.method}")
    
    try:
        doctor = crud_doctor.get_doctor_by_email(db, email=form_data.username)
        if not doctor:
            logger.warning(f"Doctor not found: {form_data.username}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        if not verify_password(form_data.password, doctor.hashed_password):
            logger.warning(f"Invalid password for doctor: {form_data.username}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        logger.info(f"Login successful for doctor: {form_data.username}")
        access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            subject=str(doctor.id), expires_delta=access_token_expires
        )
        
        response = {
            "access_token": access_token,
            "token_type": "bearer",
            "doctor_type": doctor.doctor_type
        }
        logger.debug(f"Sending response: {response}")
        return response
        
    except Exception as e:
        logger.error(f"Error during login: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.options("/register")
async def register_options():
    return JSONResponse(
        content={"message": "OK"},
        headers={
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "POST, OPTIONS",
            "Access-Control-Allow-Headers": "Content-Type, Authorization",
        },
    )

@router.post("/register", response_model=DoctorSchema)
async def register_doctor(
    *,
    db: Session = Depends(get_db),
    doctor_in: DoctorCreate,
) -> Doctor:
    """
    Register a new doctor.
    Public endpoint for registering new resident doctors.
    """
    try:
        logger.info(f"Registration attempt for email: {doctor_in.email}")
        logger.info(f"Registration data: {doctor_in.model_dump(exclude={'password'})}")
        
        # Check if email already exists
        doctor = crud_doctor.get_doctor_by_email(db, email=doctor_in.email)
        if doctor:
            logger.warning(f"Email already registered: {doctor_in.email}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )
        
        # Set doctor type to resident by default for public registration
        doctor_in.doctor_type = DoctorType.RESIDENT
        logger.info(f"Setting doctor type to RESIDENT for {doctor_in.email}")
        
        # For residents, we'll assign the first available consultant as their supervisor
        if doctor_in.doctor_type == DoctorType.RESIDENT and not doctor_in.supervisor_id:
            consultant = crud_doctor.get_doctors(
                db, 
                doctor_type=DoctorType.CONSULTANT,
                limit=1
            )
            if consultant:
                doctor_in.supervisor_id = consultant[0].id
                logger.info(f"Assigned supervisor {consultant[0].id} to {doctor_in.email}")
            else:
                logger.warning("No consultants available for supervision")
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="No consultants available to supervise. Please contact the administrator."
                )
        
        # Create the doctor
        doctor = crud_doctor.create_doctor(db=db, doctor=doctor_in)
        logger.info(f"Successfully registered new doctor: {doctor.email} (ID: {doctor.id})")
        return doctor
        
    except ValueError as e:
        logger.error(f"Validation error during registration: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error during registration: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred during registration. Please try again later."
        )

@router.options("/me")
async def me_options():
    return JSONResponse(
        content={"message": "OK"},
        headers={
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "GET, OPTIONS",
            "Access-Control-Allow-Headers": "Content-Type, Authorization",
        },
    )

@router.get("/me", response_model=DoctorSchema)
async def read_doctor_me(
    current_doctor: Doctor = Depends(get_current_doctor)
) -> Doctor:
    """
    Get current doctor.
    """
    return current_doctor
