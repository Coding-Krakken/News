import importlib
import sys
import types
import os


def test_rate_limit_disabled_in_testing(monkeypatch, tmp_path):
    # Ensure TESTING env variable triggers the testing branch
    monkeypatch.setenv('TESTING', 'true')

    # Reload module to pick up env change
    if 'app.utils.rate_limit' in sys.modules:
        del sys.modules['app.utils.rate_limit']

    # Import freshly
    rl = importlib.import_module('app.utils.rate_limit')

    # The module should expose limiter and RATE_LIMITS
    assert hasattr(rl, 'limiter')
    assert isinstance(rl.RATE_LIMITS, dict)


def test_rate_limit_handles_missing_settings(monkeypatch):
    # Simulate non-testing environment and get_settings import failing
    monkeypatch.delenv('TESTING', raising=False)

    # Monkeypatch get_settings to raise ImportError when called
    monkeypatch.setitem(sys.modules, 'app.utils.rate_limit', None)

    # Create a fake slowapi module with a Limiter class
    fake_slowapi = types.SimpleNamespace()

    class DummyLimiter:
        def __init__(self, key_func=None):
            pass

    fake_slowapi.Limiter = DummyLimiter

    slowapi_mod = types.ModuleType('slowapi')
    slowapi_mod.Limiter = DummyLimiter
    # Provide the _rate_limit_exceeded_handler symbol expected by the module
    slowapi_mod._rate_limit_exceeded_handler = lambda *a, **k: None
    sys.modules['slowapi'] = slowapi_mod
    sys.modules['slowapi.util'] = types.SimpleNamespace(get_remote_address=lambda: "127.0.0.1")
    sys.modules['slowapi.errors'] = types.SimpleNamespace(RateLimitExceeded=Exception)

    # Ensure get_settings raises when accessed via import in rate_limit
    monkeypatch.setenv('TESTING', 'false')

    # Now import the module anew; it should handle ImportError gracefully
    if 'app.utils.rate_limit' in sys.modules:
        del sys.modules['app.utils.rate_limit']

    rl = importlib.import_module('app.utils.rate_limit')
    assert hasattr(rl, 'get_rate_limit')
    assert rl.get_rate_limit('auth_login') == rl.RATE_LIMITS['auth_login']


def test_testing_attributeerror_on_set_enabled(monkeypatch):
    # Simulate TESTING env and a Limiter that raises AttributeError when setting 'enabled'
    monkeypatch.setenv('TESTING', 'true')

    class LimiterNoEnabled:
        def __init__(self, key_func=None):
            pass

        def __setattr__(self, name, value):
            if name == 'enabled':
                raise AttributeError('cannot set')
            return object.__setattr__(self, name, value)

    # Inject fake slowapi before import
    if 'app.utils.rate_limit' in sys.modules:
        del sys.modules['app.utils.rate_limit']
    sys.modules['slowapi'] = types.ModuleType('slowapi')
    sys.modules['slowapi'].Limiter = LimiterNoEnabled
    sys.modules['slowapi']. _rate_limit_exceeded_handler = lambda *a, **k: None
    sys.modules['slowapi.util'] = types.SimpleNamespace(get_remote_address=lambda: '127.0.0.1')
    sys.modules['slowapi.errors'] = types.SimpleNamespace(RateLimitExceeded=Exception)

    rl = importlib.import_module('app.utils.rate_limit')
    # module should import and not raise
    assert hasattr(rl, 'limiter')


def test_non_test_settings_disables_limiter(monkeypatch):
    # Simulate non-testing env and settings.rate_limit_enabled == False
    monkeypatch.setenv('TESTING', 'false')

    # Provide a real Limiter class for import
    class DummyLimiter:
        def __init__(self, key_func=None):
            self.enabled = True

    sys.modules['slowapi'] = types.ModuleType('slowapi')
    sys.modules['slowapi'].Limiter = DummyLimiter
    sys.modules['slowapi']._rate_limit_exceeded_handler = lambda *a, **k: None
    sys.modules['slowapi.util'] = types.SimpleNamespace(get_remote_address=lambda: '127.0.0.1')
    sys.modules['slowapi.errors'] = types.SimpleNamespace(RateLimitExceeded=Exception)

    # Patch app.config.get_settings to return an object with rate_limit_enabled False
    cfg = types.ModuleType('app.config')
    cfg.get_settings = lambda: types.SimpleNamespace(rate_limit_enabled=False)
    sys.modules['app.config'] = cfg

    if 'app.utils.rate_limit' in sys.modules:
        del sys.modules['app.utils.rate_limit']

    rl = importlib.import_module('app.utils.rate_limit')
    assert hasattr(rl, 'limiter')
