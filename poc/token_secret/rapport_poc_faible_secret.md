# Rapport de Preuve de Concept (PoC) : Enthropie du secret de signature des tokens de session faible

## 1. Informations Générales
* **Thèmes de vulnérabilité :** Token de session
* **Gravité :** Élevée

---

## 2. Localisation de la Faille
* **Composant vulnérable :** `/app/config.py`
* **Ligne où se situe la faille :** Ligne 4
* **Élément vulnérable :** `TOKEN_SECRET`

---

## 3. Description de la Faille
Le `TOKEN_SECRET` utilisé pour signer les tokens de session présente une entropie très faible. `polytech` est un mot banal, court et trop prévisible, ce qui affaiblit la sécurité de l'implémentation. Si le secret avait été un autre mot du dictionnaire de moins d'une douzaine de caractères, le résultat de la sécurité globale aurait été le même.
---

## 4. Étapes de Reproduction (Proof of Concept)
La signature des tokens étant un HMAC-SHA256 généré à partir d'un secret prévisible, un attaquant peut intercepter un token valide et tester hors-ligne une liste de mots courants pour retrouver rapidement la clé secrète.

1. **Récupération d'un token de session :** 
Prenons le token suivant : `YWxpY2V8MTc5MzM3MDQzMA==.2680ce47bd21780a5a16741c3485e925dcc060b125dddcf6654f39fe4c0600fb`

2. **Préparation / Obtention d'une liste de mot courrant :**
Ici on va créer une courte liste pour la Poc mais il existe des WordLists que l'on peut téléchargées en ligne comme SecLists. 
```python
liste = ["secret","password","admin","default","mines","test","polytech","azerty","école","polytech2027"]
```
3. **Execution du script d'exploitation:**
Une fois écrit, on peut exécuter notre script d'exploitation `poc_faible_secret.py`.

---

## 5. Impact
* **Attaque par force brute et dictionnaire :** En raison de la prévisibilité de la clé, un attaquant ayant intercepté un token valide peut retrouver le secret par force brute. Une fois le secret compromis, l'attaquant est en mesure de falsifier n'importe quel payload, de générer des signatures HMAC valides et d'usurper l'identité d'utilisateurs.
---

## 6. Remédiation
Pour corriger cette vulnérabilité, il est impératif d'utiliser un secret cryptographique fort, doté d'une forte entropie, et de stocker ce secret en dehors du code source avec une variable d'environnement ou un fichier `.env`.

De plus, pour éviter que le secret ne se régénère aléatoirement à chaque redémarrage, ce qui invaliderait toutes les sessions actives des utilisateurs, l'application doit lever une erreur critique et refuser de démarrer si la variable n'est pas explicitement définie.

Le script de démarrage automatisé start.sh a été mis en place pour gérer proprement l'environnement et s'assurer que le secret est correctement configuré :