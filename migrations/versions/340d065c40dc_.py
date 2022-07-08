"""empty message

Revision ID: 340d065c40dc
Revises: a7aec6576cca
Create Date: 2022-07-08 20:05:09.862144

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '340d065c40dc'
down_revision = 'a7aec6576cca'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('patient', sa.Column('symptoms', sa.String(), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('patient', 'symptoms')
    # ### end Alembic commands ###
