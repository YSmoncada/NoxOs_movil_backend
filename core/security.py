from datetime import datetime, timedelta
import secrets
import bcrypt

# Configuración de seguridad (Opaque Tokens)
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24 * 7 # 7 días para session token

def verify_password(plain_password: str, hashed_password: str) -> bool:
    # bcrypt.checkpw requiere bytes
    return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))

def get_password_hash(password: str) -> str:
    # Generar salt y luego el hash, debe guardarse como string en DB
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')


def create_opaque_token():
    """Genera un token opaco seguro de 64 caracteres"""
    return secrets.token_urlsafe(64)
