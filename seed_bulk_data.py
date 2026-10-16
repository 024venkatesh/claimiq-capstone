import random
from datetime import datetime, timedelta

from database import SessionLocal, engine, Base
from models import Policy, Claim

Base.metadata.create_all(bind=engine)

db = SessionLocal()

REGIONS = ["North", "South", "East", "West", "Central"]
CLAIM_TYPES = ["motor", "health", "property"]
STATUSES = ["submitted", "validation", "assigned", "under_review", "approved", "rejected", "closed"]

# Create 10 policies if not already present
policies = []
for i in range(10):
    policy_number = f"POL-BULK-{i:03d}"
    existing = db.query(Policy).filter(Policy.policy_number == policy_number).first()
    if existing:
        policies.append(existing)
        continue

    policy = Policy(
        policy_number=policy_number,
        policy_type=random.choice(CLAIM_TYPES),
        coverage_amount=round(random.uniform(5000, 100000), 2),
        region=random.choice(REGIONS),
        status="active",
        start_date=datetime.utcnow().date() - timedelta(days=random.randint(30, 500)),
        end_date=datetime.utcnow().date() + timedelta(days=random.randint(30, 500)),
    )
    db.add(policy)
    db.commit()
    db.refresh(policy)
    policies.append(policy)

# Create 100 claims
for i in range(100):
    policy = random.choice(policies)
    submitted_days_ago = random.randint(0, 30)

    claim = Claim(
        claim_number=f"CLM-BULK-{i:04d}",
        policy_id=policy.id,
        claimant_name=f"Claimant {i}",
        claim_type=policy.policy_type,
        region=policy.region,
        amount=round(random.uniform(500, 50000), 2),
        status=random.choice(STATUSES),
        submitted_at=datetime.utcnow() - timedelta(days=submitted_days_ago),
    )
    db.add(claim)

db.commit()
print("✅ Bulk data created: 10 policies, 100 claims")
db.close()