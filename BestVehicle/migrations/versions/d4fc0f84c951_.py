"""empty message

Revision ID: d4fc0f84c951
Revises: d2908717a566
Create Date: 2024-06-15 14:12:04.275819

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'd4fc0f84c951'
down_revision = 'd2908717a566'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('vehicle', schema=None) as batch_op:
        batch_op.add_column(sa.Column('name', sa.String(length=50), nullable=False))
        batch_op.drop_column('make')
        batch_op.drop_column('model')

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('vehicle', schema=None) as batch_op:
        batch_op.add_column(sa.Column('model', sa.VARCHAR(length=20), nullable=False))
        batch_op.add_column(sa.Column('make', sa.VARCHAR(length=20), nullable=False))
        batch_op.drop_column('name')

    # ### end Alembic commands ###