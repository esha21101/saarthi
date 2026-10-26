from typing import Literal

from pydantic import BaseModel, Field

CONFIRM_HELP = "True only after the caller clearly said yes to this specific action"


class StatementBody(BaseModel):
    loan_id: int
    period: Literal["last_month", "last_3_months", "last_6_months"]
    confirmed: bool = Field(description=CONFIRM_HELP)


class BlockCardBody(BaseModel):
    reason: Literal["lost", "stolen", "fraud_suspected", "other"]
    confirmed: bool = Field(description=CONFIRM_HELP)


class AddressBody(BaseModel):
    new_address: str = Field(min_length=10, max_length=200)
    confirmed: bool = Field(description=CONFIRM_HELP)


class HandoffBody(BaseModel):
    reason: str = Field(min_length=3, max_length=200)