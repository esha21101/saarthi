import secrets
import time
from datetime import date

from fastapi import Depends, FastAPI, Header, HTTPException
from psycopg.types.json import Jsonb
from pydantic import BaseModel

from app.db import get_connection
from app.models import AddressBody, BlockCardBody, HandoffBody, StatementBody

app = FastAPI(title="Saarthi Bank Backend")

SESSION_TTL_SECONDS = 15 * 60
MAX_VERIFY_ATTEMPTS = 3
SESSIONS = {}  # session_id -> {"customer_id": ..., "expires": ...}
ATTEMPTS = {}  # phone -> number of failed verifications


def current_customer(x_session_id: str = Header(...)):
    session = SESSIONS.get(x_session_id)
    if session is None or session["expires"] < time.time():
        raise HTTPException(status_code=401, detail="Not verified")
    return session["customer_id"]


def log_event(session_id: str, customer_id: int | None, event: str, details: dict):
    with get_connection() as conn:
        conn.execute(
            "INSERT INTO call_logs (session_id, customer_id, event, details) "
            "VALUES (%s, %s, %s, %s)",
            (session_id, customer_id, event, Jsonb(details)),
        )


def mask_email(email: str) -> str:
    name, domain = email.split("@")
    return f"{name[0]}***@{domain}"


class VerifyBody(BaseModel):
    phone: str
    dob: date


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/verify")
def verify(body: VerifyBody):
    if ATTEMPTS.get(body.phone, 0) >= MAX_VERIFY_ATTEMPTS:
        raise HTTPException(status_code=423, detail="Too many failed attempts")
    with get_connection() as conn:
        customer = conn.execute(
            "SELECT id, full_name FROM customers WHERE phone = %s AND dob = %s",
            (body.phone, body.dob),
        ).fetchone()
    if not customer:
        ATTEMPTS[body.phone] = ATTEMPTS.get(body.phone, 0) + 1
        log_event("unverified", None, "verify_failed", {})
        raise HTTPException(status_code=401, detail="Verification failed")
    ATTEMPTS.pop(body.phone, None)
    session_id = secrets.token_urlsafe(16)
    SESSIONS[session_id] = {
        "customer_id": customer["id"],
        "expires": time.time() + SESSION_TTL_SECONDS,
    }
    log_event(session_id, customer["id"], "verify", {"ok": True})
    return {"session_id": session_id, "name": customer["full_name"]}


@app.get("/loans")
def my_loans(customer_id: int = Depends(current_customer)):
    with get_connection() as conn:
        loans = conn.execute(
            "SELECT * FROM loans WHERE customer_id = %s", (customer_id,)
        ).fetchall()
    return {"loans": loans}


@app.post("/statements/send")
def send_statement(
    body: StatementBody,
    x_session_id: str = Header(...),
    customer_id: int = Depends(current_customer),
):
    if not body.confirmed:
        raise HTTPException(status_code=400, detail="Caller must confirm first")
    with get_connection() as conn:
        loan = conn.execute(
            "SELECT id FROM loans WHERE id = %s AND customer_id = %s",
            (body.loan_id, customer_id),
        ).fetchone()
        if not loan:
            raise HTTPException(status_code=404, detail="Loan not found")
        email = conn.execute(
            "SELECT email FROM customers WHERE id = %s", (customer_id,)
        ).fetchone()["email"]
        conn.execute(
            "INSERT INTO statements (customer_id, loan_id, period, sent_to) "
            "VALUES (%s, %s, %s, %s)",
            (customer_id, body.loan_id, body.period, email),
        )
    log_event(
        x_session_id,
        customer_id,
        "send_statement",
        {"loan_id": body.loan_id, "period": body.period},
    )
    return {"status": "sent", "sent_to": mask_email(email)}


@app.get("/card")
def card_status(customer_id: int = Depends(current_customer)):
    with get_connection() as conn:
        row = conn.execute(
            "SELECT card_status FROM customers WHERE id = %s", (customer_id,)
        ).fetchone()
    return {"card_status": row["card_status"]}


@app.post("/card/block")
def block_card(
    body: BlockCardBody,
    x_session_id: str = Header(...),
    customer_id: int = Depends(current_customer),
):
    if not body.confirmed:
        raise HTTPException(status_code=400, detail="Caller must confirm first")
    with get_connection() as conn:
        row = conn.execute(
            "SELECT card_status FROM customers WHERE id = %s", (customer_id,)
        ).fetchone()
        if row["card_status"] == "blocked":
            return {"status": "already_blocked"}
        conn.execute(
            "UPDATE customers SET card_status = 'blocked' WHERE id = %s",
            (customer_id,),
        )
    log_event(x_session_id, customer_id, "block_card", {"reason": body.reason})
    return {"status": "blocked"}


@app.post("/address")
def update_address(
    body: AddressBody,
    x_session_id: str = Header(...),
    customer_id: int = Depends(current_customer),
):
    if not body.confirmed:
        raise HTTPException(status_code=400, detail="Caller must confirm first")
    with get_connection() as conn:
        conn.execute(
            "UPDATE customers SET address = %s WHERE id = %s",
            (body.new_address, customer_id),
        )
    log_event(x_session_id, customer_id, "update_address", {"updated": True})
    return {"status": "updated"}


@app.post("/handoff")
def handoff(
    body: HandoffBody,
    x_session_id: str = Header(...),
    customer_id: int = Depends(current_customer),
):
    log_event(x_session_id, customer_id, "handoff", {"reason": body.reason})
    return {"status": "transferring"}