# BOT NSI - Discord

Lien pour ajouter et tester le bot directement sur votre serveur : https://discord.com/oauth2/authorize?client_id=1163559157157347410&permissions=8797704547392&integration_type=0&scope=bot

Un bot Discord éducatif développé en Python qui parcours les notions du programme NSI (Numérique et Sciences Informatiques) au lycée.  
Il permet de jouer à des quiz organisés par thème et par niveau (Première / Terminale), avec explication à chaque réponse.

##  Fonctionnalités

-  Quiz interactif sur différents thèmes du programme NSI
-  Commandes personnalisées `!devinette`, `!ping`, `!vote`, `!vacances`, `!joursferies`, etc.
-  Système de rappels `!rappelmoi`, `!listrappels`, `!deleterappel`
-  Infos utilisateur `!userinfo` et serveur `!serverinfo`
-  Récupération automatique des vacances scolaires et jours fériés (Zone C - Versailles)
-  Données issues d’un fichier `questions.json` structuré

##  Fichiers

- `BOT.py` : Code principal du bot Discord
- `questions.json` : Base de données des questions
- `requirements.txt` : Fichier texte avec les prérequis 

## ▶ Lancer le bot

Installe les dépendances avec :

```bash
pip install -r requirements.txt
