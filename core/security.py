from datetime import datetime, timedelta
import secrets
from passlib.context import CryptContext

# Configuración de seguridad (Opaque Tokens)
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24 * 7 # 7 días para session token

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

def create_opaque_token():
    """Genera un token opaco seguro de 64 caracteres"""
    return secrets.token_urlsafe(64)
