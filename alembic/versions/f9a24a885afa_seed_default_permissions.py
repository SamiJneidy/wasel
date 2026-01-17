"""seed default permissions

Revision ID: f9a24a885afa
Revises: 61388d151a24
Create Date: 2026-01-16 02:29:26.977770

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'f9a24a885afa'
down_revision: Union[str, None] = '4166b1cd4a61'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


from alembic import op
import sqlalchemy as sa

def upgrade() -> None:
    conn = op.get_bind()

    permissions = {   
        "branches": ["create", "read", "update", "delete"],
        "buy_invoices": ["create", "read", "update", "delete"],
        "customers": ["create", "read", "update", "delete"],
        "invoices": ["create", "read", "update", "delete"],
        "items": ["create", "read", "update", "delete"],
        "organizations": ["create", "read", "update", "delete"],
        "points_of_sale": ["create", "read", "update", "delete"],
        "projects": ["create", "read", "update", "delete"],
        "sale_invoices": ["create", "read", "update", "delete"],
        "suppliers": ["create", "read", "update", "delete"],
        "users": ["create", "read", "update", "delete"],
    }

    data = [
        {
            "resource": resource,
            "action": action,
            "description": f"Allows user to {action} {resource.replace('_', ' ')}",
        }
        for resource, actions in permissions.items()
        for action in actions
    ]

    conn.execute(
        sa.text("""
            INSERT INTO permissions (resource, action, description)
            VALUES (:resource, :action, :description)
            ON CONFLICT DO NOTHING
        """),
        data
    )



def downgrade() -> None:
    """Downgrade schema."""
    pass
