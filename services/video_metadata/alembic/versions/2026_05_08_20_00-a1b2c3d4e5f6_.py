"""add queued and transcoding statuses

Revision ID: a1b2c3d4e5f6
Revises: 96f6cf8db9fa
Create Date: 2026-05-08 20:00:00
"""
from typing import Sequence, Union
from alembic import op

revision: str = 'a1b2c3d4e5f6'
down_revision: Union[str, Sequence[str], None] = '96f6cf8db9fa'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Оскільки статус зберігається як VARCHAR (native_enum=False),
    # нові значення 'queued' і 'transcoding' просто починають використовуватись —
    # жодних ALTER TYPE не потрібно.
    # Міняємо дефолт колонки на 'queued'
    op.execute("ALTER TABLE videos ALTER COLUMN status SET DEFAULT 'queued'")
    # Старі 'uploading' записи що застрягли — переводимо в queued
    op.execute("UPDATE videos SET status = 'queued' WHERE status = 'uploading'")


def downgrade() -> None:
    op.execute("ALTER TABLE videos ALTER COLUMN status SET DEFAULT 'uploading'")
    op.execute("UPDATE videos SET status = 'uploading' WHERE status IN ('queued', 'transcoding')")