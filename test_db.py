from db.database import SessionLocal
from db import models

def test_db():
    try:
        db = SessionLocal()
        users = db.query(models.Usuario).all()
        print(f"Usuarios encontrados: {len(users)}")
        products = db.query(models.Producto).all()
        print(f"Productos encontrados: {len(products)}")
        mesas = db.query(models.Mesa).all()
        print(f"Mesas encontradas: {len(mesas)}")
        db.close()
        print("DB Check: OK")
    except Exception as e:
        print(f"DB Check ERROR: {e}")

if __name__ == "__main__":
    test_db()
