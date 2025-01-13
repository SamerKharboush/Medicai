from sqlalchemy.orm import relationship

def setup_relationships(Doctor, Patient):
    Doctor.supervised_patients = relationship(
        "Patient",
        foreign_keys=[Patient.consultant_id],
        back_populates="consultant"
    )
    Doctor.assigned_patients = relationship(
        "Patient",
        foreign_keys=[Patient.current_resident_id],
        back_populates="current_resident"
    )