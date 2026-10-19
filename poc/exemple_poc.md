# Rapport de Preuve de Concept (PoC) : [Nom de la vulnérabilité]

## 1. Informations Générales
* **Date :** 19 Octobre 2026
* **Auteur :** [Votre Nom / Pseudo]
* **Cible :** [Nom de l'application / URL / Nom du script]
* **Type de vulnérabilité :** [Ex: Injection de commandes, XSS Statique, SQLi]
* **Gravité :** [Faible / Moyenne / Élevée / Critique]

---

## 2. Description de la Faille
Décrivez brièvement ce qui ne va pas dans l'application cible.
> *Exemple : L'application ne filtre pas correctement l'entrée utilisateur dans le champ de diagnostic réseau, ce qui permet d'injecter des commandes système via des caractères de séparation comme `;`.*

---

## 3. Environnement de Test
Précisez les prérequis pour reproduire le test.
* **Composant vulnérable :** `app_vulnerable.py`
* **Version du logiciel :** v1.0.0
* **Privilèges requis :** Aucun (Utilisateur anonyme)

---

## 4. Étapes de Reproduction (Proof of Concept)

Suivez les étapes ci-dessous pour reproduire la vulnérabilité :

1. Lancez l'application vulnérable avec la commande suivante :
   ```bash
   python3 app_vulnerable.py
   ```

2. Lorsque l'application demande une saisie, injectez la charge utile (*payload*) suivante :
   ```text
   8.8.8.8 ; whoami
   ```

3. Observez le résultat dans le terminal. La commande système `whoami` est exécutée avec succès.

---

## 5. Impact
Expliquez ce qu'un attaquant peut faire en exploitant cette faille.
> *Exemple : Un attaquant distant peut exécuter des commandes arbitraires sur le serveur avec les privilèges de l'utilisateur qui exécute le script. Cela peut mener à une prise de contrôle totale de la machine ou à un vol de données.*

---

## 6. Recommandation de Correction (Remédiation)
Proposez une solution pour corriger le problème.
```python
# Exemple de correction en Python utilisant une liste d'arguments sans shell=True
import subprocess

# Remplacer os.system(commande) par :
subprocess.run(["ping", "-c", "1", ip_utilisateur], shell=False)
```