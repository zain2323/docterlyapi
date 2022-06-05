"""empty message

Revision ID: 14aea205bf65
Revises: 
Create Date: 2022-06-04 01:56:45.036437

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '14aea205bf65'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('day',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=10), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_day_name'), 'day', ['name'], unique=True)
    op.create_table('qualification',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=30), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_qualification_name'), 'qualification', ['name'], unique=True)
    op.create_table('role',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('role_name', sa.String(length=20), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_role_role_name'), 'role', ['role_name'], unique=True)
    op.create_table('specialization',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=30), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_specialization_name'), 'specialization', ['name'], unique=True)
    op.create_table('user',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=64), nullable=False),
    sa.Column('email', sa.String(length=120), nullable=False),
    sa.Column('password', sa.String(length=60), nullable=False),
    sa.Column('registered_at', sa.DateTime(), nullable=False),
    sa.Column('confirmed', sa.Boolean(), nullable=False),
    sa.Column('dob', sa.Date(), nullable=False),
    sa.Column('gender', sa.String(length=8), nullable=False),
    sa.Column('role_id', sa.Integer(), nullable=False),
    sa.Column('token', sa.String(length=32), nullable=True),
    sa.Column('token_expiration', sa.DateTime(), nullable=True),
    sa.ForeignKeyConstraint(['role_id'], ['role.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_user_email'), 'user', ['email'], unique=True)
    op.create_index(op.f('ix_user_token'), 'user', ['token'], unique=True)
    op.create_table('doctor',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('description', sa.String(), nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['user_id'], ['user.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('patient',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=30), nullable=False),
    sa.Column('dob', sa.Date(), nullable=False),
    sa.Column('gender', sa.String(length=8), nullable=False),
    sa.ForeignKeyConstraint(['user_id'], ['user.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('doctor_qualfications',
    sa.Column('doctor_id', sa.Integer(), nullable=False),
    sa.Column('qualification_id', sa.Integer(), nullable=False),
    sa.Column('procurement_year', sa.Date(), nullable=False),
    sa.Column('institute_name', sa.String(), nullable=False),
    sa.ForeignKeyConstraint(['doctor_id'], ['doctor.id'], ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['qualification_id'], ['qualification.id'], ondelete='RESTRICT'),
    sa.PrimaryKeyConstraint('doctor_id', 'qualification_id')
    )
    op.create_table('doctor_specializations',
    sa.Column('doctor_id', sa.Integer(), nullable=False),
    sa.Column('specialization_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['doctor_id'], ['doctor.id'], ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['specialization_id'], ['specialization.id'], ondelete='RESTRICT'),
    sa.PrimaryKeyConstraint('doctor_id', 'specialization_id')
    )
    op.create_table('rating',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('doctor_id', sa.Integer(), nullable=False),
    sa.Column('patient_id', sa.Integer(), nullable=False),
    sa.Column('rating', sa.Integer(), nullable=False),
    sa.Column('review', sa.String(), nullable=False),
    sa.CheckConstraint('rating < 6'),
    sa.ForeignKeyConstraint(['doctor_id'], ['doctor.id'], ),
    sa.ForeignKeyConstraint(['patient_id'], ['patient.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('slot',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('day_id', sa.Integer(), nullable=False),
    sa.Column('doctor_id', sa.Integer(), nullable=True),
    sa.Column('start', sa.Time(), nullable=False),
    sa.Column('end', sa.Time(), nullable=False),
    sa.Column('consultation_fee', sa.Integer(), nullable=False),
    sa.Column('room_number', sa.Integer(), nullable=False),
    sa.Column('appointment_duration', sa.Integer(), nullable=False),
    sa.Column('num_slots', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['day_id'], ['day.id'], ),
    sa.ForeignKeyConstraint(['doctor_id'], ['doctor.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('appointment',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('slot_id', sa.Integer(), nullable=False),
    sa.Column('patient_id', sa.Integer(), nullable=False),
    sa.Column('date', sa.Date(), nullable=False),
    sa.ForeignKeyConstraint(['patient_id'], ['patient.id'], ),
    sa.ForeignKeyConstraint(['slot_id'], ['slot.id'], ),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('slot_id', 'patient_id', name='unique_appointment')
    )
    op.create_table('prescription',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('appointment_id', sa.Integer(), nullable=False),
    sa.Column('description', sa.String(), nullable=False),
    sa.ForeignKeyConstraint(['appointment_id'], ['appointment.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('medical_history',
    sa.Column('patient_id', sa.Integer(), nullable=False),
    sa.Column('prescription_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['patient_id'], ['patient.id'], ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['prescription_id'], ['prescription.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('patient_id', 'prescription_id')
    )
    op.create_table('prescribed_medicines',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('prescription_id', sa.Integer(), nullable=False),
    sa.Column('medicine_name', sa.String(), nullable=False),
    sa.Column('medicine_formula', sa.String(), nullable=False),
    sa.Column('dosage', sa.String(), nullable=False),
    sa.Column('brand', sa.String(), nullable=False),
    sa.ForeignKeyConstraint(['prescription_id'], ['prescription.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('prescribed_medicines')
    op.drop_table('medical_history')
    op.drop_table('prescription')
    op.drop_table('appointment')
    op.drop_table('slot')
    op.drop_table('rating')
    op.drop_table('doctor_specializations')
    op.drop_table('doctor_qualfications')
    op.drop_table('patient')
    op.drop_table('doctor')
    op.drop_index(op.f('ix_user_token'), table_name='user')
    op.drop_index(op.f('ix_user_email'), table_name='user')
    op.drop_table('user')
    op.drop_index(op.f('ix_specialization_name'), table_name='specialization')
    op.drop_table('specialization')
    op.drop_index(op.f('ix_role_role_name'), table_name='role')
    op.drop_table('role')
    op.drop_index(op.f('ix_qualification_name'), table_name='qualification')
    op.drop_table('qualification')
    op.drop_index(op.f('ix_day_name'), table_name='day')
    op.drop_table('day')
    # ### end Alembic commands ###