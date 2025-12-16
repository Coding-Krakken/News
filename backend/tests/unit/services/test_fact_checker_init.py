import os
from app.services.fact_checker import FactCheckingService


def test_fact_checker_sets_api_key_env(monkeypatch):
    monkeypatch.setenv("OPENAI_API_KEY", "sk-test")
    svc = FactCheckingService()
    # If env var exists, service should pick it up (no exception)
    assert svc.api_key == "sk-test"
