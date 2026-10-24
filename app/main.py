from fastapi import FastAPI
from fastapi import FastAPI, HTTPException
from app.db import get_connection
import secrets
from datetime import date

from pydantic import BaseModel

app = FastAPI(title="Saarthi Bank Backend")


@app.get("/health")
def health():
    return {"status": "ok"}

@app.get("/customers/{customer_id}/loans")
def get_loans(customer_id: int):
    with get_connection() as conn:
        loans = conn.execute(
            "SELECT * FROM loans WHERE customer_id = %s", (customer_id,)
        ).fetchall()
    if not loans:
        raise HTTPException(status_code=404, detail="No loans found")
    return {"loans": loans}


SESSIONS = {}  # session_id -> customer_id


class VerifyBody(BaseModel):
    phone: str
    dob: date


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