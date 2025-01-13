from app.models.doctor import Doctor
from app.models.patient import Patient
from sqlalchemy.orm import relationship

# Set up relationships after both models are defined
Doctor.supervised_patients = relationship(
    "Patient",
    primaryjoin="Doctor.id==Patient.consultant_id",
    backref="consultant"
)

Doctor.assigned_patients = relationship(
    "Patient",
    primaryjoin="Doctor.id==Patient.current_resident_id",
    backref="current_resident"
)