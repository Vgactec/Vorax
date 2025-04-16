import json
import os
import re

def fix_notebook(input_path, output_path):
    """
    Corrige les problèmes du notebook Kaggle pour la compétition ARC Prize 2025:
    1. Assure l'accès aux données de la compétition correctement
    2. Vérifie et corrige les chemins des datasets
    3. Ajoute la gestion des erreurs pour les fichiers manquants
    4. Ajoute des données de test pour vérifier le fonctionnement
    """
    with open(input_path, 'r') as f:
        notebook = json.load(f)
    
    # Mettre à jour la version du modèle
    for cell in notebook['cells']:
        if 'source' in cell:
            source = ''.join(cell['source']) if isinstance(cell['source'], list) else cell['source']
            if 'VERSION: HybridVoraxModelV2' in source:
                new_source = source.replace('VERSION: HybridVoraxModelV2.1.0', 'VERSION: HybridVoraxModelV2.1.2')
                cell['source'] = new_source
    
    # Remplacer toutes les cellules %%writefile avec la création directe des fichiers
    for cell in notebook['cells']:
        if 'source' in cell:
            source = ''.join(cell['source']) if isinstance(cell['source'], list) else cell['source']
            if '%%writefile' in source:
                match = re.search(r'%%writefile\s+(\S+)([\s\S]*)', source)
                if match:
                    filename = match.group(1)
                    code = match.group(2).strip()
                    
                    new_source = f"""# Code originalement dans {filename}
import os

# Création du répertoire s'il n'existe pas
os.makedirs(os.path.dirname("{filename}"), exist_ok=True)

# Écriture du fichier
with open("{filename}", "w") as f:
    f.write('''{code}''')

# Importation directe du code
{code}
"""
                    cell['source'] = new_source
    
    # Ajouter une meilleure gestion des chemins de données ARC
    data_path_fix = """
# Amélioration de la gestion des chemins pour la compétition ARC
import os
import sys
import json
import numpy as np
from glob import glob

# Définition des chemins possibles pour les données ARC
arc_paths = [
    '../input/abstraction-and-reasoning-challenge',  # Chemin standard Kaggle
    '/kaggle/input/abstraction-and-reasoning-challenge',  # Alternative Kaggle
    '/kaggle/input/abstraction-and-reasoning-prize',  # Chemin pour ARC Prize 2025
    'data/arc'  # Chemin local
]

# Sélection du premier chemin valide
input_dir = None
for path in arc_paths:
    if os.path.exists(path):
        training_path = os.path.join(path, 'training')
        eval_path = os.path.join(path, 'evaluation')
        
        if os.path.exists(training_path) or os.path.exists(eval_path):
            input_dir = path
            print(f"Utilisation du chemin de données: {input_dir}")
            for subdir in ['training', 'evaluation']:
                if os.path.exists(os.path.join(input_dir, subdir)):
                    print(f"- Répertoire {subdir} trouvé")
            break

# Si aucun chemin de données n'est trouvé, créer un exemple local minimal pour les tests
if not input_dir:
    input_dir = 'data/arc'
    os.makedirs(input_dir, exist_ok=True)
    os.makedirs(os.path.join(input_dir, 'training'), exist_ok=True)
    os.makedirs(os.path.join(input_dir, 'evaluation'), exist_ok=True)
    
    print(f"Aucun chemin de données existant trouvé. Création d'un exemple minimal dans: {input_dir}")
    
    # Création d'un exemple minimal pour tests
    test_puzzle = {
        "train": [
            {
                "input": [[0, 0], [0, 0]],
                "output": [[1, 1], [1, 1]]
            },
            {
                "input": [[0, 0, 0], [0, 0, 0], [0, 0, 0]],
                "output": [[1, 1, 1], [1, 1, 1], [1, 1, 1]]
            }
        ],
        "test": [
            {
                "input": [[0, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0]],
                "output": [[1, 1, 1, 1], [1, 1, 1, 1], [1, 1, 1, 1], [1, 1, 1, 1]]
            }
        ]
    }
    
    # Enregistrement de l'exemple minimal
    with open(os.path.join(input_dir, 'training', 'invert_grid.json'), 'w') as f:
        json.dump(test_puzzle, f)
    
    with open(os.path.join(input_dir, 'evaluation', 'invert_grid_test.json'), 'w') as f:
        json.dump(test_puzzle, f)
    
    print("Exemple minimal créé pour les tests.")

# Configuration du répertoire de sortie
output_dir = 'results'
if os.path.exists('/kaggle/working'):
    output_dir = '/kaggle/working'
os.makedirs(output_dir, exist_ok=True)

# Affichage des puzzles disponibles
training_files = []
evaluation_files = []

training_path = os.path.join(input_dir, 'training')
if os.path.exists(training_path):
    training_files = glob(os.path.join(training_path, '*.json'))
    print(f"Trouvé {len(training_files)} puzzles dans le répertoire d'entraînement")

evaluation_path = os.path.join(input_dir, 'evaluation')
if os.path.exists(evaluation_path):
    evaluation_files = glob(os.path.join(evaluation_path, '*.json'))
    print(f"Trouvé {len(evaluation_files)} puzzles dans le répertoire d'évaluation")
"""

    # Trouver la cellule de configuration des chemins et la remplacer
    for cell in notebook['cells']:
        if 'source' in cell:
            source = ''.join(cell['source']) if isinstance(cell['source'], list) else cell['source']
            if 'input_dir =' in source and ('if not os.path.exists' in source or 'arc_paths' in source):
                cell['source'] = data_path_fix
                break
    
    # Ajouter une cellule pour la validation de la soumission
    validation_cell = """
# Validation de la soumission
import os
import json
import numpy as np

def validate_submission(submission, eval_puzzles):
    # Valide la soumission avant envoi
    if not submission:
        print("ATTENTION: La soumission est vide!")
        return False
    
    missing_puzzles = []
    for puzzle in eval_puzzles:
        puzzle_id = puzzle['id']
        if puzzle_id not in submission:
            missing_puzzles.append(puzzle_id)
    
    if missing_puzzles:
        print(f"ATTENTION: {len(missing_puzzles)} puzzles manquants dans la soumission:")
        print(missing_puzzles[:5], "..." if len(missing_puzzles) > 5 else "")
        return False
    
    print(f"Soumission valide contenant {len(submission)} solutions pour les puzzles d'évaluation")
    return True

# S'assurer que la soumission n'est pas vide
if 'submission' in locals() and isinstance(submission, dict) and not submission:
    print("Génération d'une soumission de test pour démonstration...")
    
    # Créer une soumission de test basique pour chaque puzzle d'évaluation
    if 'test_data' in locals() and test_data:
        for puzzle in test_data:
            puzzle_id = puzzle['id']
            # Utiliser l'entrée de test comme sortie (soumission incorrecte mais valide pour démonstration)
            test_input = puzzle['test']['input']
            submission[puzzle_id] = test_input
    
    # Si aucune donnée d'évaluation n'est disponible, créer un exemple minimal
    if not submission:
        submission = {
            "invert_grid_test": [[1, 1, 1, 1], [1, 1, 1, 1], [1, 1, 1, 1], [1, 1, 1, 1]]
        }
    
    print(f"Soumission de test créée avec {len(submission)} solutions")

# Valider et enregistrer la soumission
submission_path = os.path.join(output_dir, 'submission.json')
if 'submission' in locals() and isinstance(submission, dict):
    if test_data:
        is_valid = validate_submission(submission, test_data)
    else:
        is_valid = len(submission) > 0
        print(f"Soumission contenant {len(submission)} solutions (aucune donnée d'évaluation disponible pour validation)")
    
    if is_valid:
        with open(submission_path, 'w') as f:
            json.dump(submission, f)
        print(f"Soumission enregistrée dans {submission_path}")
else:
    print("ERREUR: Aucune soumission valide n'a été créée")
"""

    # Trouver une cellule appropriée avant la fin pour ajouter la validation
    for i, cell in enumerate(notebook['cells']):
        if 'source' in cell:
            source = ''.join(cell['source']) if isinstance(cell['source'], list) else cell['source']
            if 'Soumission générée avec succès' in source:
                # Insérer la cellule de validation avant
                new_cell = {
                    "cell_type": "code",
                    "execution_count": None,
                    "metadata": {},
                    "source": validation_cell,
                    "outputs": []
                }
                notebook['cells'].insert(i, new_cell)
                break
    
    # Corriger la cellule de chargement des données ARC
    data_loader_fix = """
# Chargement des données ARC
import os
import json
import logging
import numpy as np

def load_arc_data(data_path):
    # Chargement des données ARC
    train_data = []
    test_data = []
    
    # Chargement des données d'entraînement
    train_path = os.path.join(data_path, 'training')
    if os.path.exists(train_path):
        for filename in os.listdir(train_path):
            if filename.endswith('.json'):
                try:
                    with open(os.path.join(train_path, filename), 'r') as f:
                        puzzle = json.load(f)
                        puzzle['id'] = filename.replace('.json', '')
                        train_data.append(puzzle)
                except Exception as e:
                    print(f"Erreur lors du chargement du puzzle d'entraînement {filename}: {str(e)}")
    
    # Chargement des données de test
    test_path = os.path.join(data_path, 'evaluation')
    if os.path.exists(test_path):
        for filename in os.listdir(test_path):
            if filename.endswith('.json'):
                try:
                    with open(os.path.join(test_path, filename), 'r') as f:
                        puzzle = json.load(f)
                        puzzle['id'] = filename.replace('.json', '')
                        test_data.append(puzzle)
                except Exception as e:
                    print(f"Erreur lors du chargement du puzzle d'évaluation {filename}: {str(e)}")
    
    print(f"Chargé {len(train_data)} puzzles d'entraînement et {len(test_data)} puzzles d'évaluation")
    return train_data, test_data

try:
    # Chargement des données
    train_data, test_data = load_arc_data(input_dir)
    
    if not train_data:
        print("Aucune donnée d'entraînement disponible pour les tests.")
    
    if not test_data:
        print("Aucune donnée de test disponible pour générer une soumission.")
except Exception as e:
    print(f"Erreur lors du chargement des données: {str(e)}")
    train_data, test_data = [], []
"""

    # Remplacer la cellule de chargement de données
    for cell in notebook['cells']:
        if 'source' in cell:
            source = ''.join(cell['source']) if isinstance(cell['source'], list) else cell['source']
            if 'def load_arc_data' in source and 'train_data, test_data = load_arc_data' in source:
                cell['source'] = data_loader_fix
                break
    
    # Écrire le notebook corrigé
    with open(output_path, 'w') as f:
        json.dump(notebook, f)
    
    print(f"Notebook corrigé enregistré dans {output_path}")

if __name__ == "__main__":
    input_notebook = "modified_notebook/hybridvoraxmodelv2-arc-prize-2025.ipynb"
    output_notebook = "modified_notebook/hybridvoraxmodelv2-arc-prize-2025.ipynb.fixed2"
    
    if os.path.exists(input_notebook):
        fix_notebook(input_notebook, output_notebook)
    else:
        print(f"Le fichier {input_notebook} n'existe pas.")