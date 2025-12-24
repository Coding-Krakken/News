import importlib
import sys
import types
import pytest


def _make_fake_slowapi():
    mod = types.ModuleType('slowapi')
    # Limiter returns a simple object without 'enabled' attribute to force AttributeError
    def Limiter(key_func=None):
        return object()
    mod.Limiter = Limiter
    mod._rate_limit_exceeded_handler = lambda *a, **k: None

    # util submodule
    util = types.ModuleType('slowapi.util')
    util.get_remote_address = lambda req: '127.0.0.1'

    # errors submodule
    errors = types.ModuleType('slowapi.errors')
    class RateLimitExceeded(Exception):
        pass
    errors.RateLimitExceeded = RateLimitExceeded

    return mod, util, errors


@pytest.mark.parametrize('testing_value', ['true'])
def test_rate_limit_attrerror_branch(monkeypatch, testing_value):
    # Inject fake slowapi modules into sys.modules so import on reload uses them
    fake, fake_util, fake_errors = _make_fake_slowapi()
    monkeypatch.setenv('TESTING', testing_value)

    sys.modules['slowapi'] = fake
    sys.modules['slowapi.util'] = fake_util
    sys.modules['slowapi.errors'] = fake_errors

    # Now reload the module under test to execute top-level logic with TESTING=true
    import app.utils.rate_limit as rl
    importlib.reload(rl)

    # If reload succeeded, the module should exist and have RATE_LIMITS
    assert hasattr(rl, 'RATE_LIMITS')

    # Cleanup: remove our fake modules to avoid polluting other tests
    # monkeypatch will restore env; remove fake modules
    for name in ('slowapi', 'slowapi.util', 'slowapi.errors'):
        if name in sys.modules:
            del sys.modules[name]

    # Reload original module to restore normal state
    import importlib as _importlib
    _importlib.reload(rl)
