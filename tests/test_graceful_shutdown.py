"""Tests for graceful shutdown configuration."""


def test_entrypoint_has_trap():
    """entrypoint.sh должен содержать trap для SIGTERM."""
    with open("entrypoint.sh") as f:
        content = f.read()
    assert "trap" in content, "entrypoint.sh should use trap for signal handling"
    assert "SIGTERM" in content, "entrypoint.sh should handle SIGTERM"


def test_entrypoint_waits_for_children():
    """entrypoint.sh должен дожидаться завершения дочерних процессов."""
    with open("entrypoint.sh") as f:
        content = f.read()
    assert "wait" in content, "entrypoint.sh should wait for background processes"
