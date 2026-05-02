import asyncio
from logging.config import fileConfig

from sqlalchemy import pool
from sqlalchemy.ext.asyncio import async_engine_from_config

from alembic import context

# 1. Імпортуємо твої налаштування та метадані моделей
# Переконайся, що шлях імпорту відповідає структурі твого проєкту
from app.core.config import settings
from db.base import Base
import db.models  # Обов'язково імпортуємо, щоб Alembic бачив моделі

# Об'єкт конфігурації Alembic
config = context.config

# 2. Встановлюємо URL бази даних безпосередньо з твого класу Settings
# Використовуємо асинхронний URL, оскільки міграції налаштовані під async engine
config.set_main_option("sqlalchemy.url", settings.DATABASE_URL_ASYNC)

# Налаштування логування
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# 3. Вказуємо метадані для підтримки 'autogenerate'
target_metadata = Base.metadata

def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode."""
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()

def do_run_migrations(connection):
    """
    Helper function to run migrations in a synchronous context 
    within an asynchronous connection.
    """
    context.configure(connection=connection, target_metadata=target_metadata)

    with context.begin_transaction():
        context.run_migrations()

async def run_migrations_online() -> None:
    """Run migrations in 'online' mode (asynchronously)."""
    
    # Створюємо асинхронний двигун на основі конфігурації
    connectable = async_engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    async with connectable.connect() as connection:
        # Використовуємо run_sync для виконання синхронних команд Alembic
        await connection.run_sync(do_run_migrations)

    await connectable.dispose()

if context.is_offline_mode():
    run_migrations_offline()
else:
    # Використовуємо asyncio для запуску асинхронної функції міграції
    asyncio.run(run_migrations_online())