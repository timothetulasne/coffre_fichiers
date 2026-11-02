"""Authentification : mots de passe et tokens de session."""

import base64
import hashlib
import hmac
import time
import os

from app.config import TOKEN_SECRET, TOKEN_TTL


# ---------------------------------------------------------------- mots de passe

def hash_password(password: str) -> str:
    """Renvoie le sel et l'empreinte stockée pour un mot de passe."""
    sel = os.urandom(16) # sel sur 16 octects pour éviter les colisions
    return f"{sel.hex()}:{hashlib.sha256(sel + password.encode()).hexdigest()}"


def verify_password(password: str, stored_hash: str) -> bool:
    sel_hex, hache_hex = stored_hash.split(":")
    sel = bytes.fromhex(sel_hex)
    hache_clc = hashlib.sha256(sel + password.encode('utf-8')).digest()
    
    # Utilisation de compare_digest pour éviter les attaques par analyse temporelle
    return hache_clc.hex() == hache_hex


# ---------------------------------------------------------------------- tokens
# Un token a la forme :   base64("<username>|<expiration>") . signature
# La signature est un HMAC-SHA256 du contenu, en hexadécimal.

def sign(payload: bytes) -> str:
    return hmac.new(TOKEN_SECRET, payload, hashlib.sha256).hexdigest()


def generate_token(username: str) -> str:
    expiration = int(time.time()) + TOKEN_TTL
    payload = f"{username}|{expiration}".encode()
    encoded = base64.urlsafe_b64encode(payload).decode()
    return encoded + "." + sign(payload)


def verify_token(token: str):
    """Renvoie le nom d'utilisateur si le token est valide, None sinon."""
    try:
        encoded, signature = token.split(".")
        payload = base64.urlsafe_b64decode(encoded)
        username, expiration = payload.decode().rsplit("|", 1)
    except ValueError:
        return None  # token mal formé

    if signature != sign(payload):
        return None
    
    temps = int(time.time())
    if temps > int(expiration) :
        return None

    return username
