"""Tests for linter and pre-commit configuration."""

import configparser


def test_pyproject_toml_exists():
    """pyproject.toml должен существовать с настройками ruff."""
    import tomllib  # Python 3.11+

    with open("pyproject.toml", "rb") as f:
        config = tomllib.load(f)
    assert "tool" in config
    assert "ruff" in config["tool"], "ruff config should be in pyproject.toml"


def test_ruff_line_length():
    """ruff должен быть настроен на разумную длину строки."""
    import tomllib

    with open("pyproject.toml", "rb") as f:
        config = tomllib.load(f)
    line_length = config["tool"]["ruff"]["line-length"]
    assert 80 <= line_length <= 120, f"line-length {line_length} should be 80-120"


def test_ruff_target_version():
    """ruff должен быть настроен на Python 3.12."""
    import tomllib

    with open("pyproject.toml", "rb") as f:
        config = tomllib.load(f)
    target = config["tool"]["ruff"]["target-version"]
    assert target == "py312"


def test_mypy_config():
    """mypy должен быть настроен в pyproject.toml."""
    import tomllib

    with open("pyproject.toml", "rb") as f:
        config = tomllib.load(f)
    assert "mypy" in config.get("tool", {}), "mypy config should be in pyproject.toml"


def test_mypy_strict():
    """mypy должен быть в strict режиме или близком к нему."""
    import tomllib

    with open("pyproject.toml", "rb") as f:
        config = tomllib.load(f)
    mypy_config = config["tool"]["mypy"]
    assert mypy_config.get("strict", False) or mypy_config.get("check_untyped_defs", False)


def test_pre_commit_config_exists():
    """.pre-commit-config.yaml должен существовать с ruff хуками."""
    import yaml

    with open(".pre-commit-config.yaml") as f:
        config = yaml.safe_load(f)
    repos = [r["repo"] for r in config["repos"]]
    assert any("astral-sh/ruff-pre-commit" in r for r in repos), "ruff pre-commit hook should be configured"


def test_pre_commit_mypy_hook():
    """.pre-commit-config.yaml должен содержать mypy хук."""
    import yaml

    with open(".pre-commit-config.yaml") as f:
        config = yaml.safe_load(f)
    repos = config["repos"]
    hooks = []
    for repo in repos:
        hooks.extend(repo.get("hooks", []))
    hook_ids = [h["id"] for h in hooks]
    assert "mypy" in hook_ids, "mypy pre-commit hook should be configured"
