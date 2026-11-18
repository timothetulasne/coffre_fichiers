import io

from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

from app.app import app, USERS, STORAGE, SHARES
from app.sharing import generate_keypair, wrap_key

OWNER, RECIPIENT = "poc_owner", "poc_recipient"
OWNER_PASSWORD, RECIPIENT_PASSWORD = "owner-pass-123", "recipient-pass-123"
PLAINTEXT = b"PoC F8: fichier confidentiel partage avec le destinataire."

client = app.test_client()

def register(username, password):
    response = client.post("/register", json={"username": username, "password": password})
    if response.status_code != 201:
        raise SystemExit(f"Inscription de {username} impossible ({response.status_code}); changez les noms.")

def login(username, password):
    response = client.post("/login", json={"username": username, "password": password})
    if response.status_code != 200:
        raise SystemExit(f"Connexion de {username} impossible ({response.status_code}).")
    return {"Authorization": "Bearer " + response.get_json()["token"]}

register(OWNER, OWNER_PASSWORD)
register(RECIPIENT, RECIPIENT_PASSWORD)
owner_headers = login(OWNER, OWNER_PASSWORD)

upload = client.post(
    "/upload", headers=owner_headers, content_type="multipart/form-data",
    data={"file": (io.BytesIO(PLAINTEXT), "secret.txt")},
)
if upload.status_code != 201:
    raise SystemExit(f"Dépôt échoué: {upload.status_code} {upload.get_data(as_text=True)}")
file_id = upload.get_json()["file_id"]
share = client.post(f"/share/{file_id}", headers=owner_headers, json={"to": RECIPIENT})
if share.status_code != 201:
    raise SystemExit(f"Partage échoué: {share.status_code} {share.get_data(as_text=True)}")

private_key = USERS[RECIPIENT]["private_key"]
share_entry = SHARES[(file_id, RECIPIENT)]
wrapped = share_entry["wrapped_key"]
blob = share_entry["blob"]

n = private_key.public_key().public_numbers().n
d = private_key.private_numbers().d
c = int.from_bytes(wrapped, "big")
m = pow(c, d, n)
file_key = m.to_bytes(32, "big")

recovered = AESGCM(file_key).decrypt(blob[:12], blob[12:], None)
print(f"[+] Clé privée de {RECIPIENT} récupérée directement depuis USERS.")
print(f"[+] Fichier partagé déchiffré : {recovered!r}")
if recovered != PLAINTEXT:
    raise SystemExit("Le clair obtenu ne correspond pas au fichier envoyé.")
print("[+] Démontrée : une lecture de USERS suffit pour accéder au partage.")
