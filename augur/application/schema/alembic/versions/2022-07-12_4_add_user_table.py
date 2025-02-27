"""Add User table

Revision ID: 4
Revises: 3
Create Date: 2022-07-12 19:59:56.923180

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '4'
down_revision = '3'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('users',
    sa.Column('user_id', sa.Integer(), nullable=False),
    sa.Column('login_name', sa.String(), nullable=False),
    sa.Column('login_hashword', sa.String(), nullable=False),
    sa.Column('email', sa.String(), nullable=False),
    sa.Column('text_phone', sa.String(), nullable=True),
    sa.Column('first_name', sa.String(), nullable=False),
    sa.Column('last_name', sa.String(), nullable=False),
    sa.Column('tool_source', sa.String(), nullable=True),
    sa.Column('tool_version', sa.String(), nullable=True),
    sa.Column('data_source', sa.String(), nullable=True),
    sa.Column('data_collection_date', postgresql.TIMESTAMP(precision=0), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=True),
    sa.PrimaryKeyConstraint('user_id'),
    sa.UniqueConstraint('email', name='user-unique-email'),
    sa.UniqueConstraint('login_name', name='user-unique-name'),
    sa.UniqueConstraint('text_phone', name='user-unique-phone'),
    schema='augur_operations'
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('users', schema='augur_operations')
    # ### end Alembic commands ###
