"""merge-heads

Revision ID: 9873ebaafeba
Revises: 2f09d7696c15, cef03df165e6
Create Date: 2026-05-09 22:28:40.334843

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '9873ebaafeba'
down_revision: Union[str, Sequence[str], None] = ('2f09d7696c15', 'cef03df165e6')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
