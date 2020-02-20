"""empty message

Revision ID: 7335a7fff6aa
Revises: 27487ac49ba9
Create Date: 2019-12-17 16:05:14.347007

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '7335a7fff6aa'
down_revision = '27487ac49ba9'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('Show', 'start_time')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('Show', sa.Column('start_time', postgresql.TIMESTAMP(), autoincrement=False, nullable=False))
    # ### end Alembic commands ###