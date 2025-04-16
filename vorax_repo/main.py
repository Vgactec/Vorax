"""
Main script to orchestrate Kaggle API testing process and notebook correction for ARC Prize 2025.
"""

import os
import sys
import time
import logging
import json
from datetime import datetime

# Configuration du logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def load_arc_data(data_path):
    """Chargement robuste des données ARC avec validation."""
    train_data = []
    test_data = []

    try:
        # Chargement des puzzles d'entraînement
        training_file = os.path.join(data_path, 'arc-agi_training_challenges.json')
        if os.path.exists(training_file):
            with open(training_file, 'r') as f:
                train_data = json.load(f)
            logging.info(f"Chargé {len(train_data)} puzzles d'entraînement")

        # Chargement des puzzles d'évaluation
        eval_file = os.path.join(data_path, 'arc-agi_evaluation_challenges.json')
        if os.path.exists(eval_file):
            with open(eval_file, 'r') as f:
                test_data = json.load(f)
            logging.info(f"Chargé {len(test_data)} puzzles d'évaluation")
    except Exception as e:
        logging.error(f"Erreur lors du chargement des données: {str(e)}")

    return train_data, test_data

def main():
    """
    Main function to execute the entire Kaggle API testing process.

    Returns:
        int: Exit code (0 for success, non-zero for failure)
    """
    start_time = time.time()
    logger.info("Starting Kaggle API testing process")

    try:
        # Étape 1: Cloner le dépôt Kaggle API
        logger.info("Step 1: Cloning Kaggle API repository")
        from clone_kaggle_api import clone_kaggle_api
        if not clone_kaggle_api():
            logger.error("Failed to clone Kaggle API repository")
            return 1

        # Étape 2: Configuration de l'API Kaggle
        logger.info("Step 2: Setting up Kaggle API")
        from setup_kaggle_api import setup_kaggle_api
        if not setup_kaggle_api():
            logger.error("Failed to set up Kaggle API")
            return 1

        # Étape 3: Tester les commandes de l'API
        logger.info("Step 3: Testing Kaggle API commands")
        from test_kaggle_api import test_kaggle_commands
        test_results = test_kaggle_commands()

        if not test_results:
            logger.error("Failed to test Kaggle API commands")
            return 1

        # Sauvegarder les résultats bruts
        os.makedirs("results", exist_ok=True)
        with open("results/raw_results.json", "w") as f:
            json.dump(test_results, f)

        # Étape 4: Générer des rapports
        logger.info("Step 4: Generating reports")
        from generate_report import generate_reports
        if not generate_reports():
            logger.error("Failed to generate reports")
            return 1

        # Étape 5: Corriger le notebook ARC
        logger.info("Step 5: Fixing ARC notebook")
        os.makedirs("modified_notebook", exist_ok=True)

        # Version minimaliste
        from fix_minimal_arc_notebook import fix_notebook as fix_minimal
        fix_minimal("arc_notebook/hybridvoraxmodelv2-arc-prize-2025.ipynb", 
                     "modified_notebook/hybridvoraxmodelv2-arc-prize-2025.ipynb.minimal")
        logger.info("Created minimal notebook at modified_notebook/hybridvoraxmodelv2-arc-prize-2025.ipynb.minimal")

        # Version optimisée V2
        from fix_arc_notebook_final_v2 import fix_notebook as fix_v2
        fix_v2("arc_notebook/hybridvoraxmodelv2-arc-prize-2025.ipynb", 
               "modified_notebook/hybridvoraxmodelv2-arc-prize-2025.ipynb.final_v2")
        logger.info("Created optimized notebook at modified_notebook/hybridvoraxmodelv2-arc-prize-2025.ipynb.final_v2")

        # Version robuste V3
        from fix_arc_notebook_final_v3 import fix_notebook as fix_v3
        fix_v3("arc_notebook/hybridvoraxmodelv2-arc-prize-2025.ipynb", 
               "modified_notebook/hybridvoraxmodelv2-arc-prize-2025.ipynb.final_v3")
        logger.info("Created robust notebook at modified_notebook/hybridvoraxmodelv2-arc-prize-2025.ipynb.final_v3")

        # Version avec apprentissage V4
        from fix_arc_notebook_with_training import fix_notebook as fix_v4
        fix_v4("arc_notebook/hybridvoraxmodelv2-arc-prize-2025.ipynb", 
               "modified_notebook/hybridvoraxmodelv2-arc-prize-2025.ipynb.final_v4")
        logger.info("Created learning notebook at modified_notebook/hybridvoraxmodelv2-arc-prize-2025.ipynb.final_v4")

        # Étape 6: Créer les métadonnées pour le kernel
        logger.info("Step 6: Creating kernel metadata")

        kernel_metadata = {
            "id": "ndarray2000/hybridvoraxmodelv2-arc-prize-2025",
            "title": "HybridVoraxModelV2 ARC Prize 2025",
            "code_file": "hybridvoraxmodelv2-arc-prize-2025.ipynb.final_v4",
            "language": "python",
            "kernel_type": "notebook",
            "is_private": True,
            "enable_gpu": False,
            "enable_internet": False,
            "dataset_sources": [],
            "competition_sources": ["arc-prize-2025"],
            "kernel_sources": []
        }

        with open("modified_notebook/kernel-metadata-final-v4.json", "w") as f:
            json.dump(kernel_metadata, f)

        # Analyser les résultats des tests
        success_count = sum(1 for result in test_results if result.get("success", False))
        success_rate = (success_count / len(test_results)) * 100 if test_results else 0

        end_time = time.time()
        execution_time = round(end_time - start_time, 2)

        logger.info("=" * 80)
        logger.info("Kaggle API Testing Summary:")
        logger.info(f"Total commands tested: {len(test_results)}")
        logger.info(f"Successful commands: {success_count}")
        logger.info(f"Failed commands: {len(test_results) - success_count}")
        logger.info(f"Success rate: {success_rate:.2f}%")
        logger.info(f"Total execution time: {execution_time} seconds")
        logger.info("=" * 80)
        logger.info("Detailed reports available at: /home/runner/workspace/results")

        return 0

    except Exception as e:
        logger.exception(f"An error occurred during the Kaggle API testing process: {str(e)}")
        return 1

if __name__ == "__main__":
    sys.exit(main())


from flask import Flask
app = Flask(__name__)

@app.route('/')
def home():
    return 'HybridVoraxModel API Server'

@app.route('/status')
def status():
    return {
        'status': 'running',
        'version': 'v4',
        'puzzles_solved': len(os.listdir(os.path.join(data_path, 'evaluation'))),
        'model_ready': True
    }

@app.route('/metrics')
def metrics():
    return {
        'memory_usage': psutil.Process().memory_info().rss / 1024 / 1024,  # MB
        'cpu_percent': psutil.Process().cpu_percent(),
        'uptime': time.time() - start_time
    }

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)