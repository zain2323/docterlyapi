"""empty message

Revision ID: f53bcae998bf
Revises: 97247c99511d
Create Date: 2022-07-03 19:38:20.934166

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'f53bcae998bf'
down_revision = '97247c99511d'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('doctor', 'image')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('doctor', sa.Column('image', sa.VARCHAR(length=32), autoincrement=False, nullable=True))
    # ### end Alembic commands ###