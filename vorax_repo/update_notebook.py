import json
import os
import re

def fix_notebook(input_path, output_path):
    """
    Corrige les problèmes du notebook Kaggle en:
    1. Remplaçant les commandes %%writefile par du code direct
    2. Améliorant la gestion des chemins de données
    3. Ajoutant la détection des puzzles de la compétition ARC
    """
    with open(input_path, 'r') as f:
        notebook = json.load(f)
    
    # Fixons la version du modèle
    for cell in notebook['cells']:
        if 'source' in cell:
            source = ''.join(cell['source']) if isinstance(cell['source'], list) else cell['source']
            if 'VERSION: HybridVoraxModelV2' in source:
                new_source = source.replace('VERSION: HybridVoraxModelV2.1.0', 'VERSION: HybridVoraxModelV2.1.1')
                cell['source'] = new_source
    
    # Remplacer les cellules %%writefile
    for cell in notebook['cells']:
        if 'source' in cell:
            source = ''.join(cell['source']) if isinstance(cell['source'], list) else cell['source']
            if '%%writefile' in source:
                match = re.search(r'%%writefile\s+(\S+)([\s\S]*)', source)
                if match:
                    filename = match.group(1)
                    code = match.group(2).strip()
                    
                    # Créer un nouveau code qui crée les répertoires et intègre le code
                    new_source = f"""# Code originalement dans {filename}
import os

# Création du répertoire s'il n'existe pas
os.makedirs(os.path.dirname("{filename}"), exist_ok=True)

# Écriture du fichier
with open("{filename}", "w") as f:
    f.write('''{code}''')

# Exécution directe du code
{code}
"""
                    cell['source'] = new_source
    
    # Ajouter une meilleure gestion des chemins de données
    data_path_fix = """
# Amélioration de la gestion des chemins pour la compétition ARC
import os
from glob import glob

# Définition des chemins possibles pour les données ARC
arc_paths = [
    '../input/abstraction-and-reasoning-challenge',  # Chemin Kaggle
    '/kaggle/input/abstraction-and-reasoning-challenge',  # Chemin Kaggle alternatif
    'data/arc'  # Chemin local
]

# Sélection du premier chemin valide
input_dir = None
for path in arc_paths:
    if os.path.exists(path):
        input_dir = path
        print(f"Utilisation du chemin de données: {input_dir}")
        break

if not input_dir:
    os.makedirs('data/arc', exist_ok=True)
    input_dir = 'data/arc'
    print(f"Aucun chemin de données existant trouvé. Création de: {input_dir}")

# Configuration du répertoire de sortie
output_dir = 'results'
if os.path.exists('/kaggle/working'):
    output_dir = '/kaggle/working'
    
# Création du répertoire de sortie s'il n'existe pas
os.makedirs(output_dir, exist_ok=True)

# Affichage des puzzles disponibles
puzzle_files = []
for root_dir in ['training', 'evaluation']:
    dir_path = os.path.join(input_dir, root_dir)
    if os.path.exists(dir_path):
        files = glob(os.path.join(dir_path, '*.json'))
        puzzle_files.extend(files)
        print(f"Trouvé {len(files)} puzzles dans {dir_path}")
"""

    # Trouver la cellule de configuration des chemins et la remplacer
    for cell in notebook['cells']:
        if 'source' in cell:
            source = ''.join(cell['source']) if isinstance(cell['source'], list) else cell['source']
            if 'input_dir =' in source and 'if not os.path.exists' in source:
                cell['source'] = data_path_fix
                break
    
    # Ajouter une section de vérification de l'environnement Kaggle
    kaggle_env_check = """
# Vérification de l'environnement Kaggle et configuration
import os
import sys

def is_kaggle_environment():
    return 'KAGGLE_KERNEL_RUN_TYPE' in os.environ

if is_kaggle_environment():
    print("Exécution dans l'environnement Kaggle")
    # Vérification de l'accès aux données de compétition
    if os.path.exists('/kaggle/input/abstraction-and-reasoning-challenge'):
        print("Accès aux données de la compétition ARC confirmé")
    else:
        print("ATTENTION: Impossible d'accéder aux données de la compétition ARC")
        print("Assurez-vous d'avoir ajouté le dataset 'abstraction-and-reasoning-challenge'")
else:
    print("Exécution dans un environnement local")
"""

    # Ajouter cette cellule au début du notebook
    for i, cell in enumerate(notebook['cells']):
        if cell['cell_type'] == 'code' and i > 1:  # Après les cellules initiales
            new_cell = {
                "cell_type": "code",
                "execution_count": None,
                "metadata": {},
                "source": kaggle_env_check,
                "outputs": []
            }
            notebook['cells'].insert(i, new_cell)
            break
    
    # Écrire le notebook corrigé
    with open(output_path, 'w') as f:
        json.dump(notebook, f)
    
    print(f"Notebook corrigé enregistré dans {output_path}")

if __name__ == "__main__":
    input_notebook = "modified_notebook/hybridvoraxmodelv2-arc-prize-2025.ipynb"
    output_notebook = "modified_notebook/hybridvoraxmodelv2-arc-prize-2025.ipynb.fixed"
    
    if os.path.exists(input_notebook):
        fix_notebook(input_notebook, output_notebook)
    else:
        print(f"Le fichier {input_notebook} n'existe pas.")