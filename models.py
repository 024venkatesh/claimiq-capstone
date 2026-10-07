from sqlalchemy import Column, String, Numeric, Date, ForeignKey, DateTime
import uuid
from datetime import datetime

from database import Base


class Policy(Base):
    __tablename__ = "policies"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    policy_number = Column(String(50), unique=True, nullable=False)
    policy_type = Column(String(50), nullable=False)
    coverage_amount = Column(Numeric(14, 2), nullable=False)
    region = Column(String(100), nullable=False)
    status = Column(String(20), default="active")
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=False)


class Claim(Base):
    __tablename__ = "claims"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    claim_number = Column(String(50), unique=True, nullable=False)
    policy_id = Column(String(36), ForeignKey("policies.id"), nullable=False)
    claimant_name = Column(String(255), nullable=False)
    claim_type = Column(String(50), nullable=False)
    region = Column(String(100), nullable=False)
    amount = Column(Numeric(14, 2), nullable=False)
    status = Column(String(30), default="submitted")
    submitted_at = Column(DateTime, default=datetime.utcnow)