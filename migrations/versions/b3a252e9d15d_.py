"""empty message

Revision ID: b3a252e9d15d
Revises: 927597b5c4a9
Create Date: 2021-09-04 15:22:16.254354

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'b3a252e9d15d'
down_revision = '927597b5c4a9'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('fish')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('fish',
    sa.Column('name', sa.TEXT(), nullable=True),
    sa.Column('species', sa.TEXT(), nullable=True),
    sa.Column('tank_number', sa.INTEGER(), nullable=True)
    )
    # ### end Alembic commands ###
