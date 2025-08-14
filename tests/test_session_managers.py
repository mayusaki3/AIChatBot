import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from common.session.server_session_manager import ServerSessionManager
from common.session.user_session_manager import UserSessionManager


def test_server_clear_session_removes_session():
    mgr = ServerSessionManager()
    mgr.set_session(123, {"provider": "test"})
    assert mgr.has_session(123)
    mgr.clear_session(123)
    assert not mgr.has_session(123)
    mgr.clear_session(123)
    assert not mgr.has_session(123)


def test_user_clear_session_removes_session():
    mgr = UserSessionManager()
    mgr.set_session(456, {"provider": "test"})
    assert mgr.has_session(456)
    mgr.clear_session(456)
    assert not mgr.has_session(456)
    mgr.clear_session(456)
    assert not mgr.has_session(456)
