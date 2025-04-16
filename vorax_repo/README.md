# Kaggle API Testing Suite

Ce projet contient des scripts Python pour cloner et tester toutes les commandes de l'API Kaggle en ligne de commande sans interface utilisateur.

## Fonctionnalités

- Clone le dépôt GitHub de l'API Kaggle
- Installe toutes les dépendances nécessaires
- Configure l'API avec les identifiants fournis
- Teste toutes les commandes de l'API Kaggle (couverture à 100%)
- Documente les résultats dans des fichiers texte et CSV
- Gère les erreurs et les cas limites

## Structure du Projet

- `main.py` - Script principal qui orchestre tout le processus
- `clone_kaggle_api.py` - Clone le dépôt de l'API Kaggle
- `setup_kaggle_api.py` - Configure l'environnement et les identifiants
- `test_kaggle_api.py` - Exécute tous les tests sur les commandes
- `generate_report.py` - Génère des rapports à partir des résultats
- `utils.py` - Fonctions utilitaires
- `config.py` - Configuration et constantes
- `results/` - Dossier contenant les rapports générés

## Prérequis

- Python 3.x
- GitPython
- Git installé sur le système

## Installation

Aucune installation spéciale n'est nécessaire autre que les dépendances Python :

```bash
pip install gitpython
