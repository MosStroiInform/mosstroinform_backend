"""Add document signing fields

Revision ID: add_document_signing
Revises: add_users_table
Create Date: 2025-01-15 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'add_document_signing'
down_revision = 'add_users_table'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Добавляем поля для подписания документов пользователем
    op.add_column('documents', sa.Column('signed_at', sa.DateTime(), nullable=True))
    op.add_column('documents', sa.Column('signature_url', sa.String(length=1000), nullable=True))


def downgrade() -> None:
    # Удаляем поля при откате миграции
    op.drop_column('documents', 'signature_url')
    op.drop_column('documents', 'signed_at')
