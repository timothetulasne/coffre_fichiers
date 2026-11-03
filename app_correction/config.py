import os

"""Configuration du service CoffreFichiers."""

# Clé utilisée pour signer les tokens de session (HMAC).
TOKEN_SECRET = os.environ.get("TOKEN_SECRET")
if not TOKEN_SECRET:
    raise RuntimeError("pas de secret de signature présent")

# Durée de validité d'un token, en secondes.
TOKEN_TTL = 3600

# Clé maître du service, à partir de laquelle sont dérivées les clés utilisateurs.
MASTER_KEY = bytes.fromhex("6b1f0c3e9a7d4e2f8c5b1a0d3e6f9c2b")

# Taille des clés RSA générées pour le partage de fichiers.
RSA_KEY_SIZE = 2048
RSA_PUBLIC_EXPONENT = 65537
