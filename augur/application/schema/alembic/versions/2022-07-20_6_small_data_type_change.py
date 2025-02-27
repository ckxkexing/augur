"""Small data type change to match foreign key data types

Revision ID: 6
Revises: 5
Create Date: 2022-07-20 08:30:42.657758

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '6'
down_revision = '5'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('repo_sbom_scans', 'repo_id',
               existing_type=sa.INTEGER(),
               type_=sa.BigInteger(),
               existing_nullable=True,
               schema='augur_data')
    op.alter_column('repo_topic', 'repo_id',
               existing_type=sa.INTEGER(),
               type_=sa.BigInteger(),
               existing_nullable=True,
               schema='augur_data')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('repo_topic', 'repo_id',
               existing_type=sa.BigInteger(),
               type_=sa.INTEGER(),
               existing_nullable=True,
               schema='augur_data')
    op.alter_column('repo_sbom_scans', 'repo_id',
               existing_type=sa.BigInteger(),
               type_=sa.INTEGER(),
               existing_nullable=True,
               schema='augur_data')
    # ### end Alembic commands ###
