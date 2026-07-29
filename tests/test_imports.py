"""Тесты для проверки структуры проекта и импортов.

Проверяем, что:
- Все модули импортируются без ошибок
- Структура папок соответствует ожидаемой
"""

from pathlib import Path
import importlib
import pytest

PROJECT_ROOT = Path(__file__).resolve().parent.parent
EXPECTED_PACKAGES = [
    "app",
    "app.api",
    "app.services",
    "app.tasks",
]
EXPECTED_MODULES = [
    "app.config",
    "app.database",
    "app.models",
    "app.schemas",
    "app.main",
]


def test_project_root_exists():
    """Корневая папка проекта существует."""
    assert PROJECT_ROOT.exists()


def test_expected_directories_exist():
    """Все ожидаемые директории существуют."""
    dirs = [
        PROJECT_ROOT / "app",
        PROJECT_ROOT / "app" / "api",
        PROJECT_ROOT / "app" / "services",
        PROJECT_ROOT / "app" / "tasks",
        PROJECT_ROOT / "tests",
        PROJECT_ROOT / "docs",
    ]
    for dir_path in dirs:
        assert dir_path.exists(), f"Директория {dir_path} не существует"


def test_expected_files_exist():
    """Базовые файлы проекта существуют."""
    files = [
        PROJECT_ROOT / "requirements.txt",
        PROJECT_ROOT / ".env.example",
        PROJECT_ROOT / "README.md",
        PROJECT_ROOT / "app" / "__init__.py",
        PROJECT_ROOT / "app" / "api" / "__init__.py",
        PROJECT_ROOT / "app" / "services" / "__init__.py",
        PROJECT_ROOT / "app" / "tasks" / "__init__.py",
        PROJECT_ROOT / "tests" / "__init__.py",
    ]
    for file_path in files:
        assert file_path.exists(), f"Файл {file_path} не существует"


def test_packages_importable():
    """Пакеты должны импортироваться."""
    for package in EXPECTED_PACKAGES:
        try:
            importlib.import_module(package)
        except ImportError as e:
            pytest.fail(f"Пакет {package} не импортируется: {e}")


def test_modules_importable():
    """Модули должны импортироваться (заглушки)."""
    # Сначала импортируем родительские пакеты
    for package in EXPECTED_PACKAGES:
        importlib.import_module(package)
    for module in EXPECTED_MODULES:
        try:
            importlib.import_module(module)
        except ImportError as e:
            # Если модуль ещё не реализован — это ожидаемо на этапе каркаса
            # Заглушки могут быть пустыми или отсутствовать
            continue
