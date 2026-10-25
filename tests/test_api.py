from fastapi.testclient import TestClient

from app.main import app
from app.db import get_connection
from app.main import ATTEMPTS, SESSIONS, app

client = TestClient(app)


def login():
    r = client.post("/verify", json={"phone": "8964384771", "dob": "1993-11-27"})
    assert r.status_code == 200
    return {"x-session-id": r.json()["session_id"]}


def test_wrong_dob_is_rejected():
    r = client.post("/verify", json={"phone": "8964384771", "dob": "1963-11-27"})
    assert r.status_code == 401


def test_loans_need_a_valid_session():
    r = client.get("/loans", headers={"x-session-id": "abc"})
    assert r.status_code == 401


def test_loans_returns_only_own_loans():
    r = client.get("/loans", headers=login())
    assert r.status_code == 200
    assert len(r.json()["loans"]) == 2


def test_statement_needs_confirmation():
    body = {"loan_id": 1, "period": "last_month", "confirmed": False}
    r = client.post("/statements/send", json=body, headers=login())
    assert r.status_code == 400


def test_cannot_request_another_customers_loan():
    body = {"loan_id": 3, "period": "last_month", "confirmed": True}
    r = client.post("/statements/send", json=body, headers=login())
    assert r.status_code == 404


def test_invalid_period_is_rejected():
    body = {"loan_id": 1, "period": "last_year", "confirmed": True}
    r = client.post("/statements/send", json=body, headers=login())
    assert r.status_code == 422
    
def test_block_card_needs_confirmation():
    body = {"reason": "lost", "confirmed": False}
    r = client.post("/card/block", json=body, headers=login())
    assert r.status_code == 400


def test_block_card_rejects_invalid_reason():
    body = {"reason": "because", "confirmed": True}
    r = client.post("/card/block", json=body, headers=login())
    assert r.status_code == 422
    
def test_address_needs_confirmation():
    body = {"new_address": "5 Lake View Road, Pune 411001", "confirmed": False}
    r = client.post("/address", json=body, headers=login())
    assert r.status_code == 400


def test_address_too_short_is_rejected():
    body = {"new_address": "abc", "confirmed": True}
    r = client.post("/address", json=body, headers=login())
    assert r.status_code == 422


def test_handoff_needs_a_session():
    r = client.post("/handoff", json={"reason": "wants a human"}, headers={"x-session-id": "abc"})
    assert r.status_code == 401
    
def test_verify_success_is_logged():
    login()
    with get_connection() as conn:
        logs = conn.execute(
            "SELECT * FROM call_logs WHERE event = 'verify'"
        ).fetchall()
    assert len(logs) == 1


def test_statement_success_is_saved_and_logged():
    body = {"loan_id": 1, "period": "last_month", "confirmed": True}
    r = client.post("/statements/send", json=body, headers=login())
    assert r.status_code == 200
    assert r.json()["sent_to"] == "a***@yahoo.com"
    with get_connection() as conn:
        saved = conn.execute("SELECT * FROM statements").fetchall()
        logs = conn.execute(
            "SELECT * FROM call_logs WHERE event = 'send_statement'"
        ).fetchall()
    assert len(saved) == 1
    assert len(logs) == 1


def test_block_card_twice_is_idempotent():
    headers = login()
    body = {"reason": "lost", "confirmed": True}
    first = client.post("/card/block", json=body, headers=headers)
    second = client.post("/card/block", json=body, headers=headers)
    assert first.json()["status"] == "blocked"
    assert second.json()["status"] == "already_blocked"
    assert client.get("/card", headers=headers).json()["card_status"] == "blocked"


def test_address_update_changes_the_address():
    new = "5 Lake View Road, Pune 411001"
    body = {"new_address": new, "confirmed": True}
    r = client.post("/address", json=body, headers=login())
    assert r.status_code == 200
    with get_connection() as conn:
        row = conn.execute("SELECT address FROM customers WHERE id = 1").fetchone()
    assert row["address"] == new


def test_handoff_is_logged():
    r = client.post("/handoff", json={"reason": "wants a human"}, headers=login())
    assert r.status_code == 200
    with get_connection() as conn:
        logs = conn.execute(
            "SELECT * FROM call_logs WHERE event = 'handoff'"
        ).fetchall()
    assert len(logs) == 1
    
def test_lockout_after_three_wrong_attempts():
    wrong = {"phone": "8964384771", "dob": "1963-11-27"}
    for _ in range(3):
        assert client.post("/verify", json=wrong).status_code == 401
    right = {"phone": "8964384771", "dob": "1993-11-27"}
    assert client.post("/verify", json=right).status_code == 423


def test_expired_session_is_rejected():
    headers = login()
    SESSIONS[headers["x-session-id"]]["expires"] = 0
    assert client.get("/loans", headers=headers).status_code == 401