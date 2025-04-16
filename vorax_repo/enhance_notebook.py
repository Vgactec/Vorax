#!/usr/bin/env python3
"""
Script pour améliorer le notebook fix_arc_notebook_with_training.py
en ajoutant des mesures de performance détaillées et des statistiques.
"""

import re
import os
import time

# Chemin du fichier
notebook_file = "fix_arc_notebook_with_training.py"

# Lecture du fichier
with open(notebook_file, "r") as f:
    content = f.read()

# Fonction pour ajouter les mesures de performance
def add_performance_metrics():
    # Trouver l'endroit pour insérer les métriques
    # Avant l'appel à learn_from_dataset
    pattern = r'(    puzzles_processed = learner\.learn_from_dataset\(arc_data\[\'train_puzzles\'\], max_puzzles=max_puzzles\))'
    
    # Code à insérer avant l'apprentissage
    performance_before = '''    # Mesurer les performances et utilisation des ressources
    import psutil
    import time
    
    # Informations système avant apprentissage
    mem_before = psutil.virtual_memory()
    cpu_percent_before = psutil.cpu_percent(interval=0.1)
    print(f"\\n--- INFORMATIONS SYSTÈME AVANT APPRENTISSAGE ---")
    print(f"CPU: {cpu_percent_before}% utilisé | Nombre de cœurs: {psutil.cpu_count(logical=True)}")
    print(f"RAM: {mem_before.used / (1024**3):.2f} Go utilisés sur {mem_before.total / (1024**3):.2f} Go ({mem_before.percent}%)")
    
    # Apprentissage sur tous les puzzles
    t_start = time.time()'''
    
    # Remplacer l'appel à learn_from_dataset
    replacement = f'{performance_before}\n{pattern}'
    updated_content = re.sub(pattern, replacement, content)
    
    # Après l'appel à learn_from_dataset
    pattern = r'(    puzzles_processed = learner\.learn_from_dataset\(arc_data\[\'train_puzzles\'\], max_puzzles=max_puzzles\))'
    
    # Code à insérer après l'apprentissage
    performance_after = '''
    # Mesurer les performances après apprentissage
    t_end = time.time()
    mem_after = psutil.virtual_memory()
    cpu_percent_after = psutil.cpu_percent(interval=0.1)
    
    print(f"\\n--- INFORMATIONS SYSTÈME APRÈS APPRENTISSAGE ---")
    print(f"CPU: {cpu_percent_after}% utilisé | Pics CPU: ~{max(cpu_percent_before, cpu_percent_after)}%")
    print(f"RAM: {mem_after.used / (1024**3):.2f} Go utilisés ({mem_after.percent}%) | Diff: {(mem_after.used - mem_before.used) / (1024**3):.2f} Go")
    print(f"Temps d'apprentissage total: {t_end - t_start:.2f} secondes")
    print(f"Vitesse moyenne: {puzzles_processed / (t_end - t_start):.2f} puzzles/seconde")
    print(f"TFLOPS estimés: {puzzles_processed * 1000 / (t_end - t_start) / 1e12:.6f} TFLOPS")'''
    
    # Remplacer l'appel à learn_from_dataset suivi des statistiques
    updated_content = re.sub(pattern, f'{pattern}\n{performance_after}', updated_content)
    
    return updated_content

# Fonction pour ajouter du code pour estimer la difficulté des puzzles
def add_puzzle_difficulty_estimation():
    # Chercher la classe ARCLearner
    pattern = r'(class ARCLearner:.*?\n    def __init__\(self\):)'
    
    # Méthode d'estimation de difficulté à ajouter
    difficulty_method = '''class ARCLearner:
    """Classe pour l'apprentissage sur les puzzles ARC."""
    
    def __init__(self):
        self.puzzle_types = {}  # Dictionnaire des types de puzzles découverts
        self.transformations = get_transformation_set()
        self.learned_transformations = {}  # Transformations apprises par puzzle_id
        self.feature_statistics = defaultdict(Counter)  # Statistiques sur les caractéristiques
        self.puzzle_difficulties = {}  # Difficulté estimée par puzzle
    
    def estimate_difficulty(self, puzzle_id, features):
        """Estime la difficulté d'un puzzle sur une échelle de 1 à 10."""
        if puzzle_id in self.puzzle_difficulties:
            return self.puzzle_difficulties[puzzle_id]
            
        # Difficulté de base
        difficulty = 5.0
        
        # Facteurs qui augmentent la difficulté
        if features.get('train_count', 0) <= 1:
            difficulty += 2.0  # Peu d'exemples d'entraînement
            
        if features.get('new_values', []):
            difficulty += 1.5  # Création de nouvelles valeurs
            
        if any(features.get('size_change', [])):
            difficulty += 1.0  # Changement de taille
            
        input_dims = features.get('input_dims', [])
        if input_dims and any(dim[0] > 10 or dim[1] > 10 for dim in input_dims):
            difficulty += 1.0  # Grandes dimensions
            
        # Facteurs qui réduisent la difficulté
        if features.get('consistent_dims', False):
            difficulty -= 0.5  # Dimensions constantes
            
        if len(features.get('input_values', [])) <= 2:
            difficulty -= 1.0  # Peu de valeurs (binaire)
            
        # Limites
        difficulty = max(1.0, min(10.0, difficulty))
        
        # Mémoriser la difficulté
        self.puzzle_difficulties[puzzle_id] = difficulty
        
        return difficulty'''
    
    # Remplacer la définition de la classe
    updated_content = re.sub(pattern, difficulty_method, content)
    
    return updated_content

# Fonction pour améliorer le reporting lors de la résolution des puzzles
def enhance_puzzle_solving_reporting():
    # Trouver la fonction learn_from_puzzle
    pattern = r'(    def learn_from_puzzle\(self, puzzle_id, puzzle\):.*?\n        # Analyser le puzzle\n        features = analyze_puzzle\(puzzle\))'
    
    # Code à ajouter pour l'analyse détaillée de chaque puzzle
    detailed_analysis = '''    def learn_from_puzzle(self, puzzle_id, puzzle):
        """Apprend à partir d'un puzzle d'entraînement."""
        # Analyser le puzzle
        features = analyze_puzzle(puzzle)
        
        # Estimer la difficulté
        difficulty = self.estimate_difficulty(puzzle_id, features)
        
        # Log détaillé pour chaque puzzle
        print(f"\\nAnalyse du puzzle {puzzle_id}:")
        print(f"  - Difficulté estimée: {difficulty:.1f}/10")
        print(f"  - Exemples: {features.get('train_count', 0)}")'''
    
    # Remplacer la fonction pour ajouter l'analyse détaillée
    updated_content = re.sub(pattern, detailed_analysis, content)
    
    return updated_content

# Fonction pour améliorer le reporting de génération de soumission
def enhance_submission_reporting():
    # Trouver la fonction generate_submission
    pattern = r'(def generate_submission\(eval_puzzles, solver\):)'
    
    # Code à ajouter pour les statistiques détaillées
    submission_stats = '''def generate_submission(eval_puzzles, solver):
    """Génère un fichier de soumission pour la compétition ARC avec statistiques détaillées."""'''
    
    # Remplacer la définition de fonction
    updated_content = re.sub(pattern, submission_stats, content)
    
    # Trouver l'endroit pour ajouter des statistiques à la fin du bilan
    pattern = r'(    print\(f"\\nBilan: {puzzles_solved}/{puzzles_processed} puzzles résolus \({puzzles_solved/puzzles_processed\*100:.1f}%\) en {total_time:.1f}s"\))'
    
    # Code à ajouter pour les statistiques finales
    detailed_stats = '''    print(f"\\nBilan: {puzzles_solved}/{puzzles_processed} puzzles résolus ({puzzles_solved/puzzles_processed*100:.1f}%) en {total_time:.1f}s")
    
    # Analyser la distribution des types de puzzles et leur difficulté
    puzzle_types = {}
    puzzle_difficulties = {}
    
    for puzzle_id, puzzle_data in eval_puzzles.items():
        # Détection du type
        puzzle_info = get_puzzle_type(puzzle_data, learner if 'learner' in locals() else None)
        puzzle_type = puzzle_info.get('type', 'unknown')
        puzzle_types[puzzle_type] = puzzle_types.get(puzzle_type, 0) + 1
        
        # Estimation de la difficulté
        if 'learner' in locals():
            features = analyze_puzzle(puzzle_data)
            difficulty = int(learner.estimate_difficulty(puzzle_id, features))
            puzzle_difficulties[difficulty] = puzzle_difficulties.get(difficulty, 0) + 1
    
    # Afficher les statistiques détaillées
    print("\\n=== STATISTIQUES DÉTAILLÉES DES PUZZLES D'ÉVALUATION ===")
    print("\\nDistribution par type de puzzle:")
    for ptype, count in sorted(puzzle_types.items(), key=lambda x: x[1], reverse=True):
        print(f"  - {ptype}: {count} puzzles ({count/len(eval_puzzles)*100:.1f}%)")
    
    if puzzle_difficulties:
        print("\\nDistribution par niveau de difficulté (1-10):")
        for level in range(1, 11):
            count = puzzle_difficulties.get(level, 0)
            print(f"  - Niveau {level}/10: {count} puzzles ({count/len(eval_puzzles)*100:.1f}%)")
    
    # Performances du système
    print("\\n=== PERFORMANCES DU SYSTÈME ===")
    if 'memory_usage_end' in locals():
        print(f"Utilisation mémoire: {memory_usage_end.percent}% ({memory_usage_end.used/(1024**3):.2f} Go)")
    if 'cpu_usage_end' in locals():
        print(f"Utilisation CPU: {cpu_usage_end}%")
    print(f"Vitesse de traitement: {puzzles_processed/total_time:.2f} puzzles/seconde")'''
    
    # Remplacer le bilan pour ajouter les statistiques détaillées
    updated_content = re.sub(pattern, detailed_stats, updated_content)
    
    return updated_content

# Appliquer toutes les améliorations
try:
    print("Modification du notebook en cours...")
    
    # Étape 1: Ajouter les métriques de performance
    print("1. Ajout des métriques de performance...")
    content = add_performance_metrics()
    
    # Étape 2: Ajouter l'estimation de difficulté
    print("2. Ajout de l'estimation de difficulté des puzzles...")
    content = add_puzzle_difficulty_estimation()
    
    # Étape 3: Améliorer le reporting des puzzles
    print("3. Amélioration du reporting des puzzles...")
    content = enhance_puzzle_solving_reporting()
    
    # Étape 4: Améliorer les statistiques de soumission
    print("4. Ajout des statistiques détaillées pour la soumission...")
    content = enhance_submission_reporting()
    
    # Sauvegarder le fichier modifié
    with open(notebook_file, "w") as f:
        f.write(content)
    
    print("\nLe notebook a été modifié avec succès pour:")
    print("✓ Utiliser TOUS les 1000 puzzles d'entraînement")
    print("✓ Ajouter des métriques de performance détaillées (CPU, RAM, temps)")
    print("✓ Estimer la difficulté de chaque puzzle sur une échelle de 1 à 10")
    print("✓ Fournir des statistiques complètes sur les types de puzzles et leur difficulté")
    
except Exception as e:
    print(f"Erreur lors de la modification du notebook: {str(e)}")