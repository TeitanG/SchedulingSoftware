"""require positive service prices (no free services)

Revision ID: 8353b73d7dd1
Revises: 0b9d904842cc
Create Date: 2026-11-23 18:51:27.608077

Alembic autogenerate does not detect changes inside CHECK constraints,
so this migration is written by hand.
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "8353b73d7dd1"
down_revision: Union[str, Sequence[str], None] = "0b9d904842cc"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    bind = op.get_bind()
    free_services = bind.execute(
        sa.text("SELECT count(*) FROM services WHERE price_amount <= 0")
    ).scalar_one()
    if free_services:
        raise RuntimeError(
            f"Cannot upgrade: {free_services} service(s) have price_amount <= 0. "
            "Update their prices manually first."
        )

    op.drop_constraint("services_price_non_negative", "services", type_="check")
    op.create_check_constraint(
        "services_price_positive", "services", "price_amount > 0"
    )


def downgrade() -> None:
    """Downgrade schema."""
    # Relaxing the rule (> 0 to >= 0) cannot lose data.
    op.drop_constraint("services_price_positive", "services", type_="check")
    op.create_check_constraint(
        "services_price_non_negative", "services", "price_amount >= 0"
    )
