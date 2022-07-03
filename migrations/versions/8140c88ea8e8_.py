"""empty message

Revision ID: 8140c88ea8e8
Revises: 
Create Date: 2022-07-03 12:21:48.240396

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '8140c88ea8e8'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('prescribed_medicines')
    op.drop_table('medical_history')
    op.drop_table('prescription')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('prescribed_medicines',
    sa.Column('id', sa.INTEGER(), autoincrement=True, nullable=False),
    sa.Column('prescription_id', sa.INTEGER(), autoincrement=False, nullable=False),
    sa.Column('medicine_name', sa.VARCHAR(), autoincrement=False, nullable=False),
    sa.Column('medicine_formula', sa.VARCHAR(), autoincrement=False, nullable=False),
    sa.Column('dosage', sa.VARCHAR(), autoincrement=False, nullable=False),
    sa.Column('brand', sa.VARCHAR(), autoincrement=False, nullable=False),
    sa.ForeignKeyConstraint(['prescription_id'], ['prescription.id'], name='prescribed_medicines_prescription_id_fkey'),
    sa.PrimaryKeyConstraint('id', name='prescribed_medicines_pkey')
    )
    op.create_table('prescription',
    sa.Column('id', sa.INTEGER(), server_default=sa.text("nextval('prescription_id_seq'::regclass)"), autoincrement=True, nullable=False),
    sa.Column('appointment_id', sa.INTEGER(), autoincrement=False, nullable=False),
    sa.Column('description', sa.VARCHAR(), autoincrement=False, nullable=False),
    sa.ForeignKeyConstraint(['appointment_id'], ['appointment.id'], name='prescription_appointment_id_fkey'),
    sa.PrimaryKeyConstraint('id', name='prescription_pkey'),
    postgresql_ignore_search_path=False
    )
    op.create_table('medical_history',
    sa.Column('patient_id', sa.INTEGER(), autoincrement=False, nullable=False),
    sa.Column('prescription_id', sa.INTEGER(), autoincrement=False, nullable=False),
    sa.ForeignKeyConstraint(['patient_id'], ['patient.id'], name='medical_history_patient_id_fkey', ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['prescription_id'], ['prescription.id'], name='medical_history_prescription_id_fkey', ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('patient_id', 'prescription_id', name='medical_history_pkey')
    )
    # ### end Alembic commands ###
