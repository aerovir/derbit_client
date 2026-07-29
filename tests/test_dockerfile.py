"""Tests for Dockerfile multi-stage build."""


def test_dockerfile_has_multiple_stages():
    """Dockerfile должен использовать multi-stage build (несколько FROM)."""
    with open("Dockerfile") as f:
        content = f.read()
    from_count = content.count("FROM ")
    assert from_count >= 2, f"Expected >= 2 FROM statements, got {from_count}"


def test_dockerfile_runtime_stage_slim():
    """Runtime stage должен использовать slim образ."""
    with open("Dockerfile") as f:
        content = f.read()
    # Найти последний FROM (runtime stage)
    stages = [line for line in content.split("\n") if line.strip().startswith("FROM ")]
    runtime_stage = stages[-1]
    assert "slim" in runtime_stage, f"Runtime stage should use slim image: {runtime_stage}"


def test_dockerfile_has_non_root_user():
    """Runtime stage должен содержать non-root пользователя."""
    with open("Dockerfile") as f:
        content = f.read()
    assert "USER" in content, "Dockerfile should set a non-root USER"


def test_dockerfile_copies_venv_only():
    """Dockerfile должен копировать виртуальное окружение из build stage."""
    with open("Dockerfile") as f:
        content = f.read()
    assert "COPY --from=" in content, "Dockerfile should copy from build stage"
