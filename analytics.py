import pandas as pd
from datetime import datetime
from sqlalchemy.orm import Session

from models import Claim


def build_claims_analytics(db: Session) -> dict:
    claims = db.query(Claim).all()

    if not claims:
        return {
            "total_claims": 0,
            "approval_rate": 0.0,
            "rejection_rate": 0.0,
            "avg_turnaround_hours": 0.0,
            "sla_breached_count": 0,
            "volume_by_region": {},
            "volume_by_claim_type": {},
        }

    # Convert claims (SQLAlchemy objects) into a list of dictionaries for Pandas
    records = []
    for c in claims:
        records.append({
            "id": c.id,
            "region": c.region,
            "claim_type": c.claim_type,
            "status": c.status,
            "amount": float(c.amount),
            "submitted_at": c.submitted_at,
        })

    df = pd.DataFrame(records)

    # Handle duplicates/missing values (good practice, matches SRS Section 14)
    df = df.drop_duplicates(subset=["id"])
    df["region"] = df["region"].fillna("Unknown")
    df["claim_type"] = df["claim_type"].fillna("Unknown")

    total = len(df)
    approved = int((df["status"] == "approved").sum())
    rejected = int((df["status"] == "rejected").sum())

    approval_rate = round(approved / total, 4) if total else 0.0
    rejection_rate = round(rejected / total, 4) if total else 0.0

    # Turnaround time: for now, use time since submission (since we don't have closed_at yet)
    now = pd.Timestamp(datetime.utcnow())
    df["hours_open"] = (now - df["submitted_at"]).dt.total_seconds() / 3600
    avg_turnaround = round(df["hours_open"].mean(), 2)

    # SLA breach: claims open longer than 72 hours and not yet closed
    SLA_HOURS = 72
    open_statuses = ["submitted", "validation", "assigned", "under_review"]
    sla_breached = int(
        ((df["status"].isin(open_statuses)) & (df["hours_open"] > SLA_HOURS)).sum()
    )

    volume_by_region = df.groupby("region").size().to_dict()
    volume_by_claim_type = df.groupby("claim_type").size().to_dict()

    return {
        "total_claims": total,
        "approval_rate": approval_rate,
        "rejection_rate": rejection_rate,
        "avg_turnaround_hours": avg_turnaround,
        "sla_breached_count": sla_breached,
        "volume_by_region": volume_by_region,
        "volume_by_claim_type": volume_by_claim_type,
    }