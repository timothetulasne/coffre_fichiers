# CoffreFichiers

Service interne de stockage de fichiers chiffrés.

```
coffre_fichiers/
├── app/                  # service initial (vulnérable)
│   ├── app.py            #   endpoints Flask
│   ├── auth.py           #   mots de passe et tokens
│   ├── config.py         #   paramètres et secrets
│   ├── crypto_utils.py   #   chiffrement des fichiers
│   └── sharing.py        #   partage de fichiers (RSA)
├── app_correction/       # service sécurisé (version corrigée)
├── exemples/             # fichiers de test
├── start.sh              # script d'automatisation du lancement
└── .env                  # variables d'environnement (secrets)
```

## 1. Configuration des secrets (`.env`)

Avant de lancer l'application, assurez-vous d'avoir un fichier `.env` à la racine contenant vos clés secrètes :

```env
TOKEN_SECRET=be38e23a0b1746a363c0f2f007b3e9b04c78e76192f798c792f3313e2544fd3a
MASTER_KEY=6b1f0c3e9a7d4e2f8c5b1a0d3e6f9c2b
```

## 2. Installation et Lancement avec `start.sh`

Le script `start.sh` automatise la création de l'environnement virtuel, l'installation des dépendances, le chargement du `.env` et le démarrage du serveur.

Rendez le script exécutable (si ce n'est pas déjà fait) puis lancez-le :

```bash
chmod +x start.sh
./start.sh
```

Le service démarre sur **http://127.0.0.1:5000** (en utilisant la version sécurisée `app_correction.app`).

---

## 3. Utilisation de l'API (à lancer dans un autre terminal)

**Créer deux comptes**

```bash
curl -X POST http://127.0.0.1:5000/register -H "Content-Type: application/json" \
     -d '{"username":"alice","password":"motdepasse-alice"}'
curl -X POST http://127.0.0.1:5000/register -H "Content-Type: application/json" \
     -d '{"username":"bob","password":"motdepasse-bob"}'
```

**Se connecter**

```bash
curl -X POST http://127.0.0.1:5000/login -H "Content-Type: application/json" \
     -d '{"username":"alice","password":"motdepasse-alice"}'
# {"token":"YWxpY2V8MTc2..."}
TOKEN_A="<token d'alice>"
```

**Déposer, lister, télécharger**

```bash
curl -X POST http://127.0.0.1:5000/upload -H "Authorization: Bearer $TOKEN_A" \
     -F "file=@exemples/rapport.txt"
# {"file_id":"file-1","len":...}

curl http://127.0.0.1:5000/files -H "Authorization: Bearer $TOKEN_A"
curl http://127.0.0.1:5000/download/file-1 -H "Authorization: Bearer $TOKEN_A" -o sortie.txt
```

**Partager un fichier et consulter une clé publique**

```bash
curl -X POST http://127.0.0.1:5000/share/file-1 -H "Authorization: Bearer $TOKEN_A" \
     -H "Content-Type: application/json" -d '{"to":"bob"}'
curl http://127.0.0.1:5000/pubkey/bob
```

Bob peut ensuite télécharger `file-1` avec son propre token.

## Endpoints disponibles

| Endpoint | Méthode | Authentifié | Description |
|---|---|---|---|
| `/register` | POST | non | Crée un compte (`username`, `password`) |
| `/login` | POST | non | Renvoie un token de session |
| `/pubkey/<username>` | GET | non | Clé publique RSA d'un utilisateur |
| `/upload` | POST | oui | Dépose un fichier (chiffré avant stockage) |
| `/files` | GET | oui | Liste ses fichiers et ceux partagés avec soi |
| `/download/<file_id>` | GET | oui | Télécharge un fichier en clair |
| `/share/<file_id>` | POST | oui | Partage un de ses fichiers (`{"to": "<username>"}`) |

Le stockage est en mémoire : tout est perdu à l'arrêt du service.