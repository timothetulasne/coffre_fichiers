# Rapport de Preuve de Concept (PoC) : Non vérification de l'expiration du token de session

## 1. Informations Générales
* **Thèmes de vulnérabilité :** Token de session
* **Gravité :** Élevée

---

## 2. Localisation de la Faille
* **Composant vulnérable :** `/app/auth.py`
* **Ligne où se situe la faille :** Ligne 37
* **Élément vulnérable :** `verify_token()`

---

## 3. Description de la Faille
La vérification de la durée de vie du token de session `TOKEN_TTL` n'est pas effectuée par la fonction `verify_token()`. Bien que la date d'expiration soit extraite, aucune logique de contrôle ne compare ce timestamp à l'heure actuelle du système.

Cette implémentation présente deux faiblesses majeures :
1. **Validité infinie :** Un token généré reste indéfiniment valide pour effectuer des actions authentifiées. Le `TOKEN_TTL` n'a alors plus d'intérêt.
2. **Persistence du risque :** La révocation temporelle est inopérante ; tout token compromis reste réutilisable sans limite dans le temps.
---

## 4. Étapes de Reproduction (Proof of Concept)

1. **Obtention des données :** 
   Génération légitime d'un token à l'instant T0 par l'utilisateur `alice`. Le token est calculé avec un TTL court (3600 secondes).
   '''text
   Token généré à T0 : YWxpY2V8MTc5MzM3MDQzMA==.2680ce47bd21780a5a16741c3485e925dcc060b125dddcf6654f39fe4c0600fb
   Timestamp d'expiration contenu : 1793370430
   ```

2. **Préparation du scénario :** 
   Attendre le dépassement du délai de validité théorique (T_actuel > T_expiration) afin de simuler l'utilisation d'un token obsolète.
   >Ici, le token a été généré le 30/10/2026

3. **Exécution du test (PoC Python) :**
   Exécution de `poc_expiration_token.py` appelant `verify_token()` avec le token dont le timestamp d'expiration est dépassé.

4. **Résultat :** 
   La fonction `verify_token()` renvoie `alice` au lieu de `None`. La signature cryptographique étant toujours valide, l'absence de contrôle sur le timestamp d'expiration permet la validation du token.

5. **Usurpation d'identité :** 
   L'identifiant `alice` est retourné au contrôleur d'authentification, ce qui accorde l'accès aux ressources protégées sous l'identité d'Alice au moyen d'un jeton hors délai.
---

## 5. Impact
En exploitant cette vulnérabilité suite à l'interception ou la fuite d'un token de session :
- **Usurpation d'identité durable :** Un attaquant en possession d'un ancien token peut continuer à effectuer des actions authentifiées de manière permanente au nom de la victime.
- **Incapacité de rotation des sessions :** Le mécanisme de renouvellement des sessions devient inefficace pour invalider les sessions obsolètes.
---

## 6. Remédiation