# Rapport de Preuve de Concept (PoC) : Secret de signature des tokens de session stocké en dur

## 1. Informations Générales
* **Thèmes de vulnérabilité :** Token de session
* **Gravité :** Critique

---

## 2. Localisation de la Faille
* **Composant vulnérable :** `/app/config.py`
* **Ligne où se situe la faille :** Ligne 4
* **Élément vulnérable :** `TOKEN_SECRET`

---

## 3. Description de la Faille
Le `TOKEN_SECRET` est codé directement en dur dans le fichier de configuration de l'application. Une fuite du code source expose ce secret critique à des individus malveillants.

---

## 4. Étapes de Reproduction (Proof of Concept)
La mise en évidence de cette vulnérabilité est triviale : elle repose sur une inspection statique du code source de l'application.

1. **Inspection du code source :** 
   L'analyse du fichier `/app/config.py` révèle la présence du secret en clair directement assigné à la variable `TOKEN_SECRET`.
2. **Exploitation :** 
   Dès lors que le code est accessible, le secret est compromis sans qu'il soit nécessaire de lancer une attaque active ou de deviner la valeur.

---

## 5. Impact
* **Compromission totale de l'authentification :** L'accès au secret en dur permet à un attaquant de générer ou de falsifier des tokens de session valides pour n'importe quel utilisateur, entraînant une usurpation d'identité et un contournement des mécanismes de contrôle d'accès.

---

## 6. Remédiation
Pour corriger cette vulnérabilité, il est impératif d'externaliser le secret de la base de code en utilisant une variable d'environnement. 

Mais une simple génération aléatoire dans le code à chaque lancement provoquerait la perte des sessions utilisateurs en cas de redémarrage du serveur. Il convient donc de configurer le secret via un fichier `.env` ou l'environnement système, et d'interdire le démarrage de l'application si ce dernier est absent.

Pour la correction de l'application, nous avons généré un secret avec la commande `python3 -c "import secrets; print(secrets.token_hex(32))` ce qui nous a donné TOKEN_SECRET=be38e23a0b1746a363c0f2f007b3e9b04c78e76192f798c792f3313e2544fd3a à mettre dans le `.env`.

Le script de déploiement et de démarrage `start.sh` a été créé de toutes pièces pour automatiser ces vérifications de sécurité de manière robuste.

