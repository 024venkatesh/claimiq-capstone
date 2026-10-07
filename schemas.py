from pydantic import BaseModel
from datetime import date
import uuid
from datetime import datetime

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

from datetime import datetime


class ClaimNoteOut(BaseModel):
    id: str
    claim_id: str
    note: str | None
    previous_status: str | None
    new_status: str
    is_override: str
    override_justification: str | None
    created_at: datetime

    class Config:
        from_attributes = True

class UserCreate(BaseModel):
    email: str
    password: str
    full_name: str
    role: str = "support_agent"


class UserOut(BaseModel):
    id: str
    email: str
    full_name: str
    role: str

    class Config:
        from_attributes = True


class LoginRequest(BaseModel):
    email: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"