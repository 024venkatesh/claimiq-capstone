from pydantic import BaseModel
from datetime import date
import uuid


class PolicyCreate(BaseModel):
    policy_number: str
    policy_type: str
    coverage_amount: float
    region: str
    status: str = "active"
    start_date: date
    end_date: date


class PolicyOut(PolicyCreate):
    id: str

    class Config:
        from_attributes = True


class ClaimCreate(BaseModel):
    policy_id: str
    claimant_name: str
    claim_type: str
    region: str
    amount: float


class ClaimOut(ClaimCreate):
    id: str
    claim_number: str
    status: str

    class Config:
        from_attributes = True

class ClaimStatusUpdate(BaseModel):
    new_status: str
    note: str | None = None
    is_override: bool = False
    override_justification: str | None = None