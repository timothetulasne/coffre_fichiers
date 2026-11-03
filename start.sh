#!/bin/bash

set -e # arret si erreur

if [ ! -d ".venv" ]; then # si environnement virtuel pas créé
    python3 -m venv .venv
fi

source .venv/bin/activate # activation de l'environnement virtuel

if [ -f "requirements.txt" ]; then # si dépendances pas installées
    pip install --upgrade pip > /dev/null 2>&1
    pip install -q -r requirements.txt
fi

if [ -f ".env" ]; then
    set -a # activer l'exportation des variables
    source .env
    set +a # la desactiver
fi

if [ -z "$TOKEN_SECRET" ]; then # si le TOKEN_SECRET n'existe pas sur le serveur
    echo "variable d'environnemet TOKEN_SESSION pas définie dans .env"
    exit 1
fi

python -m app_correction.app # démarrage application