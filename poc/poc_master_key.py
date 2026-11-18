import hashlib

from app.app import STORAGE
from app.config import MASTER_KEY
from app.crypto_utils import decrypt_bytes, derive_user_key

USERNAME = "alice"
FILE_ID = "file-1"

entry = STORAGE.get(FILE_ID)
if entry is None:
    raise SystemExit(
        f"Fichier {FILE_ID!r} absent de STORAGE. Déposez d'abord un fichier "
        "avec le compte local correspondant, puis ajustez USERNAME/FILE_ID."
    )
if entry["owner"] != USERNAME:
    raise SystemExit(f"{FILE_ID} appartient à {entry['owner']!r}, pas à {USERNAME!r}.")

recovered_key = hashlib.sha256(MASTER_KEY + USERNAME.encode()).digest()
assert recovered_key == derive_user_key(USERNAME)

plaintext = decrypt_bytes(entry["blob"], recovered_key)
print(f"[+] Clé AES de {USERNAME!r} recalculée depuis MASTER_KEY.")
print(f"[+] Fichier {FILE_ID!r} déchiffré : {plaintext!r}")
print("[+] F4 démontrée : le mot de passe du compte n’a pas été utilisé.")
