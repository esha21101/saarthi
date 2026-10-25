from fastapi.testclient import TestClient

from app.main import app

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