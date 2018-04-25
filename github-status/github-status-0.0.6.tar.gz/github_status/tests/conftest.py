import os
import pytest


@pytest.fixture
def p_env(monkeypatch):
    def patch(environ):
        monkeypatch.setattr(os, 'environ', environ)
        monkeypatch.setattr(os, 'getenv', lambda x: environ.get(x))
    return patch
