# Rapport de Preuve de Concept (PoC) : Chiffrement RSA non sécurisé

## 1. Informations Générales
- **Thèmes de vulnérabilité :** Chiffrement asymétrique utilisé pour le partage
- **Gravité :** Critique

---

## 2. Localisation de la Faille
- **Composant vulnérable :** `/app/config.py` et `/app/sharing.py`
- **Lignes où se situent les failles :** 
  - Fichier `/app/config.py` : Ligne 18 (`RSA_PUBLIC_EXPONENT = 3`)
  - Fichier `/app/sharing.py` : Implémentation du chiffrement direct sans padding
- **Élément vulnérable :** Paramétrage et implémentation du chiffrement RSA (*Textbook RSA*)

---

## 3. Description de la Faille
L'application implémente un simple chiffrement RSA asymétrique pour sécuriser le partage de clés de fichiers entre utilisateurs, ce qui présente de graves lacunes cryptographiques.

Cette implémentation souffre de la combinaison de trois faiblesses majeures :
1. **Absence de padding (bourrage) :** Le code convertit directement la clé symétrique du fichier en un entier brut (`m = int.from_bytes(file_key, "big")`) sans appliquer aucun schéma de remplissage stochastique (type OAEP).
2. **Exposant public RSA trop faible :** Historiquement, un exposant $e = 3$ était utilisé pour accélérer les opérations de chiffrement. Cependant, si le schéma de remplissage est mal configuré ou absent, le système devient totalement non sécurisé. L'exposant public est ici configuré à sa valeur minimale (`RSA_PUBLIC_EXPONENT = 3`), offrant une résistance mathématique nulle face à des attaques par faible exposant.
3. **Disproportion de taille et rôle du padding :** La clé symétrique (`file_key`) fait seulement 32 octets (256 bits), tandis que le module RSA $n$ fait 2048 bits. En théorie, la taille de la clé doit correspondre à la taille du message à chiffrer (par blocs de 2048 bits). Le padding aléatoire permet de combler les clés trop courtes sans pour autant révéler la structure de la clé, grâce à son caractère stochastique. 

C'est précisément la combinaison de ces trois faiblesses d'implémentation (absence de padding, exposant faible et clé trop courte non masquée) qui crée cette vulnérabilité critique.

**Conséquence mathématique :** 
Puisque le message $m$ est très court et que l'exposant est $e = 3$, le calcul $m^3$ donne un résultat dont la valeur numérique est strictement inférieure au module $n$ ($m^3 < n$). Par conséquent, l'opération modulo $n$ dans l'équation `c = pow(m, e, n)` n'a aucun effet mathématique. Le texte chiffré $c$ est égal exactement au cube parfait du message :
$$c = m^3$$

---

## 4. Étapes de Reproduction (Proof of Concept)

1. **Interception du message chiffré :** 
   Un attaquant accède au dictionnaire global `SHARES` via une sauvegarde de la mémoire ou une interception du trafic de partage. Il récupère la valeur chiffrée de la clé (wrapped_key) (ainsi que le blob chiffré du fichier (blob) ici pour vérifier la poc).

2. **Attaque par extraction de racine :**
   Puisque $c = m^3$, l'attaquant n'a pas besoin de la clé privée RSA de la victime. Il lui suffit d'exécuter un script d'attaque (poc_rsa_faible.py) pour calculer la racine cubique entière exacte du texte chiffré, évitant ainsi les pertes de précision des nombres à virgule flottante.

3. **Validation et Déchiffrement du message :**
   Le script reconstruit la clé symétrique exacte de 32 octets et tente de déchiffrer le blob AES-GCM intercepté pour prouver la compromission des données.
---

## 5. Impact
- **Compromission de la confidentialité :** N'importe quel attaquant capable d'intercepter un message chiffré destiné à un utilisateur peut retrouver immédiatement la clé de chiffrement du fichier partagé.
- **Déchiffrement des données :** Une fois la clé de fichier récupérée, l'attaquant peut déchiffrer le blob AES-GCM associé et lire l'intégralité du contenu du fichier confidentiel.

---

## 6. Remédiation
Pour corriger ces faiblesses cryptographiques sur le chiffrement asymétrique, il convient d'utiliser un schéma de remplissage standardisé et robuste comme OAEP à la place de RSA brut, combiné à un exposant public standard sécurisé ($65537$).

**Correctifs appliqués :**
1. Modification de l'exposant public dans `config.py` : `RSA_PUBLIC_EXPONENT = 65537`.
2. Utilisation des fonctions de chiffrement haut niveau de la bibliothèque `cryptography` avec le padding OAEP dans `sharing.py`.

**Exemple de code corrigé (`sharing.py`) :**
```python
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives import hashes

def wrap_key(file_key: bytes, public_key) -> bytes:
    """Chiffre une clé de fichier avec RSA-OAEP (sécurisé)."""
    return public_key.encrypt(
        file_key,
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None
        )
    )

def unwrap_key(wrapped: bytes, private_key) -> bytes:
    """Déchiffre une clé de fichier avec RSA-OAEP."""
    return private_key.decrypt(
        wrapped,
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None
        )
    )
```