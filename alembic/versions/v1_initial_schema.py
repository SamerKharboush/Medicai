"""v1 initial schema

Revision ID: v1_initial_schema
Revises: 
Create Date: 2024-01-03 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'v1_initial_schema'
down_revision = None
branch_labels = None
depends_on = None

def upgrade():
    # Create doctors table
    op.create_table(
        'doctors',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('email', sa.String(), nullable=False),
        sa.Column('hashed_password', sa.String(), nullable=False),
        sa.Column('first_name', sa.String(50), nullable=False),
        sa.Column('last_name', sa.String(50), nullable=False),
        sa.Column('medical_license_number', sa.String(50), nullable=False),
        sa.Column('qualifications', sa.String(200), nullable=False),
        sa.Column('specialty', sa.String(50), nullable=False),
        sa.Column('subspecialty', sa.String(100)),
        sa.Column('years_of_experience', sa.Integer(), nullable=False),
        sa.Column('doctor_type', sa.String(20), nullable=False),
        sa.Column('date_of_birth', sa.Date(), nullable=False),
        sa.Column('gender', sa.String(10), nullable=False),
        sa.Column('contact_number', sa.String(20), nullable=False),
        sa.Column('emergency_contact', sa.String(20)),
        sa.Column('department', sa.String(100), nullable=False),
        sa.Column('office_location', sa.String(100)),
        sa.Column('consultation_hours', sa.String(200)),
        sa.Column('join_date', sa.Date(), nullable=False),
        sa.Column('is_active', sa.Boolean(), server_default=sa.text('true'), nullable=False),
        sa.Column('bio', sa.Text()),
        sa.Column('research_interests', sa.Text()),
        sa.Column('publications', sa.Text()),
        sa.Column('certifications', sa.Text()),
        sa.Column('supervisor_id', sa.Integer(), sa.ForeignKey('doctors.id')),
        sa.Column('graduation_date', sa.Date()),
        sa.Column('rotation_schedule', sa.Text()),
        sa.Column('teaching_responsibilities', sa.Text()),
        sa.Column('administrative_roles', sa.Text()),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('email'),
        sa.UniqueConstraint('medical_license_number')
    )
    op.create_index(op.f('ix_doctors_id'), 'doctors', ['id'], unique=False)
    op.create_index(op.f('ix_doctors_email'), 'doctors', ['email'], unique=True)

    # Create patients table
    op.create_table(
        'patients',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('age', sa.Integer()),
        sa.Column('gender', sa.String()),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.text('now()'), onupdate=sa.text('now()')),
        sa.Column('consultant_id', sa.Integer(), sa.ForeignKey('doctors.id'), nullable=False),
        sa.Column('current_resident_id', sa.Integer(), sa.ForeignKey('doctors.id')),
        sa.Column('risk_factors', postgresql.JSONB, server_default='{}'),
        sa.Column('family_history', postgresql.JSONB, server_default='[]'),
        sa.Column('surgical_history', postgresql.JSONB, server_default='[]'),
        sa.Column('additional_notes', postgresql.JSONB, server_default='[]'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_patients_id'), 'patients', ['id'], unique=False)
    op.create_index(op.f('ix_patients_name'), 'patients', ['name'], unique=False)

    # Create clinical_records table
    op.create_table(
        'clinical_records',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('patient_id', sa.Integer(), sa.ForeignKey('patients.id')),
        sa.Column('recorded_at', sa.DateTime(), server_default=sa.text('now()')),
        sa.Column('created_by_id', sa.Integer(), sa.ForeignKey('doctors.id'), nullable=False),
        sa.Column('audio_file_path', sa.String()),
        sa.Column('transcription', sa.String()),
        sa.Column('extracted_data', postgresql.JSONB),
        sa.Column('is_processed', sa.Boolean(), server_default=sa.text('false')),
        sa.Column('processing_status', sa.String()),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.text('now()'), onupdate=sa.text('now()')),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_clinical_records_id'), 'clinical_records', ['id'], unique=False)

def downgrade():
    op.drop_table('clinical_records')
    op.drop_table('patients')
    op.drop_table('doctors') 