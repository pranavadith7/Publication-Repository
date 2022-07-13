"""updated faculty fields as nullable

Revision ID: 5996797a4e0e
Revises: b4cdfae27790
Create Date: 2022-03-26 00:26:03.016966

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '5996797a4e0e'
down_revision = 'b4cdfae27790'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('faculty', 'about_me',
               existing_type=sa.TEXT(),
               nullable=True)
    op.alter_column('faculty', 'designation',
               existing_type=sa.VARCHAR(length=100),
               nullable=True)
    op.alter_column('faculty', 'department',
               existing_type=sa.VARCHAR(length=100),
               nullable=True)
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('faculty', 'department',
               existing_type=sa.VARCHAR(length=100),
               nullable=False)
    op.alter_column('faculty', 'designation',
               existing_type=sa.VARCHAR(length=100),
               nullable=False)
    op.alter_column('faculty', 'about_me',
               existing_type=sa.TEXT(),
               nullable=False)
    # ### end Alembic commands ###
