import secrets
from datetime import date

from fastapi import Depends, FastAPI, Header, HTTPException
from pydantic import BaseModel

from app.db import get_connection

from typing import Literal

app = FastAPI(title="Saarthi Bank Backend")

SESSIONS = {}  # session_id -> customer_id


def current_customer(x_session_id: str = Header(...)):
    customer_id = SESSIONS.get(x_session_id)
    if customer_id is None:
        raise HTTPException(status_code=401, detail="Not verified")
    return customer_id


class VerifyBody(BaseModel):
    phone: str
    dob: date


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/verify")
def verify(body: VerifyBody):
    with get_connection() as conn:
        customer = conn.execute(
            "SELECT id, full_name FROM customers WHERE phone = %s AND dob = %s",
            (body.phone, body.dob),
        ).fetchone()
    if not customer:
        raise HTTPException(status_code=401, detail="Verification failed")
    session_id = secrets.token_urlsafe(16)
    SESSIONS[session_id] = customer["id"]
    return {"session_id": session_id, "name": customer["full_name"]}


@app.get("/loans")
def my_loans(customer_id: int = Depends(current_customer)):
    with get_connection() as conn:
        loans = conn.execute(
            "SELECT * FROM loans WHERE customer_id = %s", (customer_id,)
        ).fetchall()
    return {"loans": loans}

def mask_email(email: str) -> str:
    name, domain = email.split("@")
    return f"{name[0]}***@{domain}"


class StatementBody(BaseModel):
    loan_id: int
    period: Literal["last_month", "last_3_months", "last_6_months"]
    confirmed: bool


@app.post("/statements/send")
def send_statement(body: StatementBody, customer_id: int = Depends(current_customer)):
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
    return {"status": "sent", "sent_to": mask_email(email)}