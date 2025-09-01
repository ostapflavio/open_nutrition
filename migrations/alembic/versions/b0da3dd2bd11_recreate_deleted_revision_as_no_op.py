"""Recreate deleted revision as no-op~

Revision ID: b0da3dd2bd11
Revises: 11c2af436e19
Create Date: 2025-08-30 17:02:01.729898

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'b0da3dd2bd11'
down_revision: Union[str, Sequence[str], None] = '11c2af436e19'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
