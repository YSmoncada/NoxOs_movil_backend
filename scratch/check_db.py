from db.database import SessionLocal, engine
from db import models
from sqlalchemy import inspect

def check_db():
    inspector = inspect(engine)
    tables = inspector.get_table_names()
    print(f"Tables in DB: {tables}")
    
    if "user_sessions" in tables:
        print("Table 'user_sessions' exists.")
    else:
        print("Table 'user_sessions' MISSING!")
        # Try to create it explicitly
        models.Base.metadata.create_all(bind=engine)
        print("Attempted to create tables.")

if __name__ == "__main__":
    check_db()
