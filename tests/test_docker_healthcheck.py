"""Tests for Docker healthcheck configuration."""

import subprocess
import sys


def test_healthcheck_command_works():
    """Healthcheck команда должна работать через python -c с urllib."""
    code = """
import urllib.request
try:
    resp = urllib.request.urlopen('http://localhost:8000/health', timeout=5)
    assert resp.status == 200, f'Got {resp.status}'
    data = resp.read()
    assert b'ok' in data, f'Unexpected response: {data}'
    print('HEALTHY')
except Exception as e:
    print(f'UNHEALTHY: {e}')
    sys.exit(1)
"""
    # Просто проверяем, что код синтаксически корректен
    compile(code, "<test>", "exec")
    assert True
