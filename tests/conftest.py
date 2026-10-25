import pytest

from app.db import get_connection
from app.main import ATTEMPTS


@pytest.fixture(autouse=True)
def clean_state():
    yield  # the test runs here, then the cleanup below runs
    with get_connection() as conn:
        conn.execute("UPDATE customers SET card_status = 'active'")
        conn.execute(
            "UPDATE customers SET address = 'New Emblem Street escape 24' WHERE id = 1"
        )
        conn.execute("DELETE FROM call_logs")
        conn.execute("DELETE FROM statements")
    ATTEMPTS.clear()