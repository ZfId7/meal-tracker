"""add optional saved meal items

Revision ID: cbb228ce897c
Revises: 0e2d677705a7
Create Date: 2026-03-13 07:13:36.556283

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'cbb228ce897c'
down_revision = '0e2d677705a7'
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table("saved_meal_items", schema=None) as batch_op:
        batch_op.add_column(
            sa.Column(
                "is_optional",
                sa.Boolean(),
                nullable=False,
                server_default=sa.false(),
            )
        )
        batch_op.alter_column(
            "amount",
            existing_type=sa.Float(),
            nullable=True,
        )
        batch_op.alter_column(
            "unit",
            existing_type=sa.String(length=20),
            nullable=True,
        )

    # ### end Alembic commands ###


def downgrade():
    with op.batch_alter_table("saved_meal_items", schema=None) as batch_op:
        batch_op.alter_column(
            "unit",
            existing_type=sa.String(length=20),
            nullable=False,
        )
        batch_op.alter_column(
            "amount",
            existing_type=sa.Float(),
            nullable=False,
        )
        batch_op.drop_column("is_optional")

    # ### end Alembic commands ###
