import hashlib

# Copie de la fonction de hachage problématique (depuis auth.py)
def hash_password(password: str) -> str:
    """Renvoie l'empreinte stockée pour un mot de passe."""
    return hashlib.sha256(password.encode()).hexdigest()

bdd_fuitee = {
    "alice": "a2986d5e1277d5730090f0d746a0d7011b51df7b4103b843d3057976582b048e",
    "bob" : "93a7e5c7e4d24ec3e0d4397a8b84274e8df7c03125389a343299d5c7a42b84b9"
}

# Dictionnaire de l'attaquant
mdp_connus = ["12345678", "motdepasse-alice", "secret2026!"]

print("-- Attaque par dictionnaire (Début) --\n")

# Boucle sur les mots de passe du dictionnaire
for mdp in mdp_connus:
    # On simule le comportement de l'application en hachant le mot de passe testé
    hache_clc = hash_password(mdp)
    
    # On compare le résultat avec chaque utilisateur de la base fuitée
    for user, hache_bdd in bdd_fuitee.items():
        if hache_bdd == hache_clc:
            print("Le mot de passe de", user,"est", mdp)

print("\n-- Attaque par dictionnaire (Fin) --")
