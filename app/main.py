import secrets
from datetime import date

from fastapi import Depends, FastAPI, Header, HTTPException
from pydantic import BaseModel

from app.db import get_connection

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