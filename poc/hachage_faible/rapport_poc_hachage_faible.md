# Rapport de Preuve de Concept (PoC) : Faible hachage des mots de passe stockés dans la base de données

## 1. Informations Générales
* **Thèmes de vulnérabilité :** Stockage de mots de passe 
* **Gravité :** Élevée

---

## 2. Localisation de la Faille
* **Composant vulnérable :** `/app/auth.py`
* **Ligne où se situe la faille :** Ligne 13
* **Élément vulnérable :** `hashlib.sha256()`

---

## 3. Description de la Faille
L'application utilise l'algorithme SHA-256 de façon brute (sans sel et sans étirement de clé) pour stocker les mots de passe des utilisateurs. 

Cette implémentation présente deux faiblesses majeures :
1. **Absence de sel :** SHA-256 est un algorithme déterministe. Un même mot de passe produira toujours la même empreinte (hash).
   > *Exemple : Le mot de passe `motdepasse-alice` génère systématiquement l'empreinte `a2986d5e1277d5730090f0d746a0d7011b51df7b4103b843d3057976582b048e`.*
2. **Rapidité d'exécution :** SHA-256 est conçu pour être très rapide à calculer. Cela permet à un attaquant d'exécuter des milliards de tentatives par seconde lors d'une attaque hors ligne.

---

## 4. Étapes de Reproduction (Proof of Concept)

1. **Obtention des données :** L'attaquante, **Eve**, récupère la base de données des comptes fuitée contenant les identifiants et leurs empreintes SHA-256 :
   * `alice` : `a2986d5e1277d5730090f0d746a0d7011b51df7b4103b843d3057976582b048e`
   * `bob` : `93a7e5c7e4d24ec3e0d4397a8b84274e8df7c03125389a343299d5c7a42b84b9`

2. **Préparation de l'attaque :** Sachant que l'application utilise SHA-256 sans sel, Eve prépare un dictionnaire de mots de passe courants (`mdp_connus = ["12345678", "motdepasse-alice", "secret2026!"]`).

3. **Exécution de l'attaque par dictionnaire (PoC Python) :**
   Eve exécute le script `poc.py` qui génère l'empreinte SHA-256 de chaque mot de passe candidat et la compare aux empreintes de la base fuitée :
   ```python
   hache_clc = hash_password(mdp)
   ```

4. **Résultat :** Le script d'Eve retrouve immédiatement le mot de passe clair de la cible :
   > `Le mot de passe de alice est motdepasse-alice`

5. **Usurpation d'identité :** Eve peut désormais se connecter sur l'application légitime en utilisant l'identifiant `alice` et le mot de passe retrouvé.

---

## 5. Impact
En exploitant cette vulnérabilité suite à une fuite de données :
* **Usurpation de compte :** Un attaquant peut compromettre l'intégralité des comptes utilisateurs dont les mots de passe figurent dans des dictionnaires ou peuvent être devinés par force brute.
* **Réutilisation de mots de passe :** L'attaquant peut essayer ces combinaisons identifiant/mot de passe sur d'autres services tiers.

---

## 6. Remédiation

Pour sécuriser le stockage des mots de passe, il est nécessaire de remplacer SHA-256 par un algorithme d'empreinte spécialisé pour les mots de passe (*Password Hashing Function*).

### Recommandations :
1. **Utiliser un algorithme robuste et lent :** Employer **Argon2id**, **Bcrypt** ou **PBKDF2**. Ces algorithmes intègrent un facteur de coût ajustable rendant les attaques par force brute extrêmement lentes et coûteuses. Ici pas utiles d'aller jusqu'à ce niveau d'exigence, on rajoute simplement un sel aléatoire au mdp avant le hachage par sha-256.
2. **Ajouter un sel unique par utilisateur (Salt) :** Générer un sel aléatoire et unique pour chaque utilisateur lors de la création ou modification du mot de passe. Cela empêche les attaques par tables d'arc-en-ciel.

### Exemple de correction dans `/app/auth.py` (avec `argon2-cffi` ou `bcrypt`) :
```python
def hash_password(password: str) -> str:
    """Renvoie le sel et l'empreinte stockée pour un mot de passe."""
    sel = os.urandom(16) # sel sur 16 octects pour éviter les colisions
    hache = hashlib.sha256(sel + password.encode('utf-8')).hexdigest()
    return f"{sel.hex()}:{hache}"


def verify_password(password: str, stored_value: str) -> bool:
    try:
        sel_hex, hache_hex = stored_value.split(":")
        salt = bytes.fromhex(salt_hex)
        hache_clc = hashlib.sha256(salt + password.encode('utf-8')).digest()
        
        # Utilisation de compare_digest pour éviter les attaques par analyse temporelle
        return hashlib.compare_digest(hache_clc.hex(), hache_hex)
    except (ValueError, AttributeError):
        return False
```

a = hash_password("motdepasse-alice")
b = hash_password("motdepasse-alice")

sel_a, hache_a = a.split(":")
sel_b, hache_b = b.split(":")
print(a,int(sel_a,16))
print("\n")
print(b,int(sel_b,16))


616c257548b15b1b7b9103411d5129bb:159b867ba757cc796e528ac24ec17ef7e96946f47c14dbc6278720e1ce73fc09
--> sel = 129496643393206281155808329900156332475

88072ede251eed3cbb886414d27d7184:d3d3846ab023419130499c277e41d27ae3a73e1633eb5bf2779b81fb02f084fb 
--> sel = 180812304095740482110992372681813094788