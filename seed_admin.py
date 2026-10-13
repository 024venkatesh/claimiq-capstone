from database import SessionLocal, engine, Base
from models import User
from security import hash_password

# Make sure tables exist
Base.metadata.create_all(bind=engine)

db = SessionLocal()

existing = db.query(User).filter(User.email == "admin@claimiq.com").first()
if existing:
    print("Admin already exists!")
else:
    admin = User(
        email="admin@claimiq.com",
        hashed_password=hash_password("Admin@123"),
        full_name="System Admin",
        role="admin",
        region=None,
    )
    db.add(admin)
    db.commit()
    print("✅ Admin user created successfully!")

db.close()