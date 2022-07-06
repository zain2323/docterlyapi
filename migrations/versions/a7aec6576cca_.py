"""empty message

Revision ID: a7aec6576cca
Revises: d3ab33728b68
Create Date: 2022-07-05 23:00:07.963882

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'a7aec6576cca'
down_revision = 'd3ab33728b68'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('specialization', sa.Column('image', sa.String(), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('specialization', 'image')
    # ### end Alembic commands ###