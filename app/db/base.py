# Import all the models, so that Base has them before being
# imported by Alembic
from app.db.base_class import Base  # noqa
from app.models.doctor import Doctor  # noqa
from app.models.patient import Patient , ClinicalRecord  # noqa
from app.models.patient_assignment import PatientAssignment  # noqa
