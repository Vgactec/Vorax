# Propriété de VoraxSolutions © 2025
# Tous droits réservés

import os
import json
import logging

logger = logging.getLogger('ARC-HybridVoraxModelV2')

def load_arc_data(data_path):
    """Chargement des données ARC."""
    train_data = []
    test_data = []
    
    # Chargement des données d'entraînement
    train_path = os.path.join(data_path, 'training')
    if os.path.exists(train_path):
        for filename in os.listdir(train_path):
            if filename.endswith('.json'):
                with open(os.path.join(train_path, filename), 'r') as f:
                    puzzle = json.load(f)
                    puzzle['id'] = filename.replace('.json', '')
                    train_data.append(puzzle)
    else:
        train_challenges_path = os.path.join(data_path, 'arc-agi_training_challenges.json')
        train_solutions_path = os.path.join(data_path, 'arc-agi_training_solutions.json')
        
        if os.path.exists(train_challenges_path) and os.path.exists(train_solutions_path):
            with open(train_challenges_path, 'r') as f:
                train_challenges = json.load(f)
            with open(train_solutions_path, 'r') as f:
                train_solutions = json.load(f)
                
            for puzzle_id, challenge in train_challenges.items():
                if puzzle_id in train_solutions:
                    puzzle = {
                        'id': puzzle_id,
                        'train': [{'input': example['input'], 'output': example['output']} 
                                  for example in challenge['train']],
                        'test': {'input': challenge['test']['input']}
                    }
                    puzzle['test']['output'] = train_solutions[puzzle_id]
                    train_data.append(puzzle)
    
    # Chargement des données de test
    test_path = os.path.join(data_path, 'evaluation')
    if os.path.exists(test_path):
        for filename in os.listdir(test_path):
            if filename.endswith('.json'):
                with open(os.path.join(test_path, filename), 'r') as f:
                    puzzle = json.load(f)
                    puzzle['id'] = filename.replace('.json', '')
                    test_data.append(puzzle)
    else:
        eval_challenges_path = os.path.join(data_path, 'arc-agi_evaluation_challenges.json')
        eval_solutions_path = os.path.join(data_path, 'arc-agi_evaluation_solutions.json')
        
        if os.path.exists(eval_challenges_path) and os.path.exists(eval_solutions_path):
            with open(eval_challenges_path, 'r') as f:
                eval_challenges = json.load(f)
            with open(eval_solutions_path, 'r') as f:
                eval_solutions = json.load(f)
                
            for puzzle_id, challenge in eval_challenges.items():
                if puzzle_id in eval_solutions:
                    puzzle = {
                        'id': puzzle_id,
                        'train': [{'input': example['input'], 'output': example['output']} 
                                  for example in challenge['train']],
                        'test': {'input': challenge['test']['input']}
                    }
                    puzzle['test']['output'] = eval_solutions[puzzle_id]
                    test_data.append(puzzle)
    
    logger.info(f"Loaded {len(train_data)} training puzzles and {len(test_data)} test puzzles")
    return train_data, test_data

# Chargement des données
train_data, test_data = load_arc_data(input_dir)