""" Add Executions

Revision ID: 5edecbbc06f1
Revises: 6cecd2318b0e
Create Date: 2018-04-26 15:45:09.628000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '5edecbbc06f1'
down_revision = '6cecd2318b0e'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table('queuedexecution',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('monitor', sa.Unicode(length=50), nullable=False),
        sa.Column('event_id', sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(['event_id'], ['event.id']),
        sa.PrimaryKeyConstraint('id')
    )


def downgrade():
    op.drop_table('queuedexecution')
