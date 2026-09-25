"""Add pipelines_moma table

Revision ID: a1c2e3f4b5d6
Revises: fb76fa161028
Create Date: 2026-06-22 15:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'a1c2e3f4b5d6'
down_revision = 'fb76fa161028'
branch_labels = None
depends_on = None


def upgrade():
    # Table dédiée à la branche de démonstration MoMa. Elle coexiste avec la
    # table `pipelines` (branche principale) sans la modifier.
    op.create_table('pipelines_moma',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=255), nullable=True),
    sa.Column('graph_json', sa.JSON(), nullable=False),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.Column('updated_at', sa.DateTime(), nullable=True),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
    sa.PrimaryKeyConstraint('id')
    )


def downgrade():
    op.drop_table('pipelines_moma')
