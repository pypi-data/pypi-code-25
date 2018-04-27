# coding: utf-8
from alembic import op
import sqlalchemy as sa


revision = '6cecd2318b0e'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.create_table('event',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('type', sa.Unicode(length=50), nullable=False),
        sa.Column('datetime', sa.DateTime(), nullable=False),
        sa.Column('body', sa.LargeBinary(), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_table('missingsincetriggerstate',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('monitor', sa.Unicode(length=50), nullable=False),
        sa.Column('last_triggered', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('monitor')
    )
    op.create_table('monitorstate',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('monitor', sa.Unicode(length=50), nullable=False),
        sa.Column('content', sa.LargeBinary(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('monitor')
    )


def downgrade():
    op.drop_table('monitorstate')
    op.drop_table('missingsincetriggerstate')
    op.drop_table('event')
