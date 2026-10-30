import time
import base64
import hmac
import hashlib

# Import des fonctions utiles pour la PoC

TOKEN_SECRET = b"polytech"
TOKEN_TTL = 3600

def sign(payload: bytes) -> str:
    return hmac.new(TOKEN_SECRET, payload, hashlib.sha256).hexdigest()

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

    # L'expiration est conservée dans le token pour un usage futur.
    return username

# PoC

token_expire = "YWxpY2V8MTc5MzM3MDQzMA==.2680ce47bd21780a5a16741c3485e925dcc060b125dddcf6654f39fe4c0600fb"

payload_encodee = token_expire.split(".")[0]
payload_decodee = base64.b64decode(payload_encodee).decode('utf-8')

timestamp = payload_decodee.split("|")[1]

print(f"Heure actuelle : {int(time.time())}")
print(f"Timestamp du token : {int(timestamp)}")

result = verify_token(token_expire)

print(f"Résultat de verify_token() : {result}")