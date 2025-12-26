import importlib
import sys
import types


def _make_fake_slowapi():
    mod = types.ModuleType("slowapi")

    def Limiter(key_func=None):
        class L:
            enabled = True

        return L()

    mod.Limiter = Limiter
    mod._rate_limit_exceeded_handler = lambda *a, **k: None

    util = types.ModuleType("slowapi.util")
    util.get_remote_address = lambda req: "127.0.0.1"

    errors = types.ModuleType("slowapi.errors")

    class RateLimitExceeded(Exception):
        pass

    errors.RateLimitExceeded = RateLimitExceeded

    return mod, util, errors


def test_rate_limit_config_import_error(monkeypatch):
    # Prepare fake slowapi so imports succeed
    fake, fake_util, fake_errors = _make_fake_slowapi()
    sys.modules["slowapi"] = fake
    sys.modules["slowapi.util"] = fake_util
    sys.modules["slowapi.errors"] = fake_errors

    # Inject a fake app.config module whose get_settings raises ImportError
    fake_config = types.ModuleType("app.config")

    def get_settings():
        raise ImportError("config load failed")

    fake_config.get_settings = get_settings
    sys.modules["app.config"] = fake_config

    # Ensure TESTING is not true
    monkeypatch.delenv("TESTING", raising=False)

    # Reload the module to execute top-level branch that should catch ImportError
    import app.utils.rate_limit as rl

    importlib.reload(rl)

    # The module should expose RATE_LIMITS even if config load failed
    assert hasattr(rl, "RATE_LIMITS")

    # Cleanup inserted modules
    for name in ("slowapi", "slowapi.util", "slowapi.errors", "app.config"):
        if name in sys.modules:
            del sys.modules[name]

    # Reload original module to restore state
    import importlib as _importlib

    _importlib.reload(rl)
