from app.db.database import SessionLocal
from app.db.schema import User

def extract_users():
    
    db = SessionLocal()

    try:
        return db.query(User).all()
    
    finally:
        db.close()