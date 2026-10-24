from fastapi import FastAPI
from fastapi import FastAPI, HTTPException
from app.db import get_connection

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