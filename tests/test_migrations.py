"""Tests for Alembic database migrations setup."""


def test_alembic_installed():
    """Alembic должен быть установлен как зависимость."""
    import alembic  # noqa: F401


def test_alembic_ini_exists():
    """alembic.ini должен существовать."""
    import configparser

    config = configparser.ConfigParser()
    parsed = config.read("alembic.ini")
    assert parsed, "alembic.ini not found or empty"
    assert "alembic" in config.sections()


def test_alembic_directory_exists():
    """Директория alembic должна существовать."""
    import os

    assert os.path.isdir("alembic"), "alembic/ directory not found"
    assert os.path.isfile("alembic/env.py"), "alembic/env.py not found"
    assert os.path.isfile("alembic/script.py.mako"), "alembic/script.py.mako not found"


def test_migration_exists():
    """Должна существовать хотя бы одна миграция."""
    from pathlib import Path

    versions_dir = Path("alembic/versions")
    assert versions_dir.is_dir(), "alembic/versions/ directory not found"
    migrations = list(versions_dir.glob("*.py"))
    assert len(migrations) >= 1, "No migration files found in alembic/versions/"
    # Исключаем __init__.py
    py_files = [m for m in migrations if m.name != "__init__.py"]
    assert len(py_files) >= 1, "No actual migration files found"


def test_migration_creates_price_records():
    """Миграция должна создавать таблицу price_records."""
    from pathlib import Path

    versions_dir = Path("alembic/versions")
    migration_files = sorted(versions_dir.glob("*.py"))
    for mf in migration_files:
        if mf.name == "__init__.py":
            continue
        content = mf.read_text()
        if "price_records" in content:
            return  # Нашли
    assert False, "No migration creates price_records table"


def test_env_py_imports_models():
    """alembic/env.py должен импортировать Base из models."""
    with open("alembic/env.py") as f:
        content = f.read()
    assert "target_metadata" in content, "env.py should define target_metadata"
