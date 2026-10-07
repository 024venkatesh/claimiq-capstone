from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
import uuid

from database import engine, Base, get_db
from models import Policy
from schemas import PolicyCreate, PolicyOut

from models import Claim
from schemas import ClaimCreate, ClaimOut
import uuid as uuid_module

from workflow import validate_transition
from schemas import ClaimStatusUpdate

from models import ClaimNote
from schemas import ClaimNoteOut

# This line creates the actual table in Postgres if it doesn't exist yet
Base.metadata.create_all(bind=engine)

app = FastAPI()


@app.get("/")
def read_root():
    return {"message": "ClaimIQ is alive!"}


@app.post("/policies", response_model=PolicyOut)
def create_policy(policy: PolicyCreate, db: Session = Depends(get_db)):
    new_policy = Policy(**policy.model_dump())
    db.add(new_policy)
    db.commit()
    db.refresh(new_policy)
    return new_policy


@app.get("/policies/{policy_id}", response_model=PolicyOut)
def get_policy(policy_id: str, db: Session = Depends(get_db)):
    policy = db.query(Policy).filter(Policy.id == policy_id).first()
    if not policy:
        raise HTTPException(status_code=404, detail="Policy not found")
    return policy


@app.get("/policies", response_model=list[PolicyOut])
def list_policies(db: Session = Depends(get_db)):
    return db.query(Policy).all()

@app.post("/claims", response_model=ClaimOut)
def create_claim(claim: ClaimCreate, db: Session = Depends(get_db)):
    # BR-002: claim must link to a valid, active policy
    policy = db.query(Policy).filter(Policy.id == claim.policy_id).first()
    if not policy:
        raise HTTPException(status_code=422, detail="Policy not found")
    if policy.status != "active":
        raise HTTPException(status_code=422, detail="Policy is not active")

    new_claim = Claim(
        claim_number=f"CLM-{uuid_module.uuid4().hex[:8].upper()}",
        policy_id=claim.policy_id,
        claimant_name=claim.claimant_name,
        claim_type=claim.claim_type,
        region=claim.region,
        amount=claim.amount,
    )
    db.add(new_claim)
    db.commit()
    db.refresh(new_claim)
    return new_claim


@app.get("/claims", response_model=list[ClaimOut])
def list_claims(db: Session = Depends(get_db)):
    return db.query(Claim).all()


@app.get("/claims/{claim_id}", response_model=ClaimOut)
def get_claim(claim_id: str, db: Session = Depends(get_db)):
    claim = db.query(Claim).filter(Claim.id == claim_id).first()
    if not claim:
        raise HTTPException(status_code=404, detail="Claim not found")
    return claim

@app.patch("/claims/{claim_id}/status", response_model=ClaimOut)
def update_claim_status(claim_id: str, payload: ClaimStatusUpdate, db: Session = Depends(get_db)):
    claim = db.query(Claim).filter(Claim.id == claim_id).first()
    if not claim:
        raise HTTPException(status_code=404, detail="Claim not found")

    if payload.is_override and not payload.override_justification:
        raise HTTPException(status_code=422, detail="Override requires a justification")

    error = validate_transition(claim.status, payload.new_status, payload.is_override)
    if error:
        raise HTTPException(status_code=422, detail=error)

    previous_status = claim.status
    claim.status = payload.new_status
    db.commit()
    db.refresh(claim)

    # BR-007: append-only history of every status change
    note_entry = ClaimNote(
        claim_id=claim.id,
        note=payload.note,
        previous_status=previous_status,
        new_status=payload.new_status,
        is_override="true" if payload.is_override else "false",
        override_justification=payload.override_justification,
    )
    db.add(note_entry)
    db.commit()

    return claim


@app.get("/claims/{claim_id}/history", response_model=list[ClaimNoteOut])
def get_claim_history(claim_id: str, db: Session = Depends(get_db)):
    claim = db.query(Claim).filter(Claim.id == claim_id).first()
    if not claim:
        raise HTTPException(status_code=404, detail="Claim not found")

    return db.query(ClaimNote).filter(ClaimNote.claim_id == claim_id).order_by(ClaimNote.created_at).all()