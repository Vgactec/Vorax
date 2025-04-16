"""
Script optimisé pour tester rapidement les fonctionnalités clés de l'API Kaggle.
"""
import os
import sys
import time
import json
import logging
from datetime import datetime
import subprocess
from pathlib import Path

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Répertoires
RESULTS_DIR = Path("results")
RESULTS_DIR.mkdir(exist_ok=True)
DOWNLOAD_DIR = Path("download_test")
DOWNLOAD_DIR.mkdir(exist_ok=True)

# Fichiers de résultats
COMMAND_RESULTS_JSON = RESULTS_DIR / "quick_results.json"
SUMMARY_REPORT = RESULTS_DIR / "quick_summary_report.txt"

def run_command(command, timeout=30):
    """Exécute une commande shell et retourne son résultat."""
    logger.info(f"Exécution: {command}")
    
    start_time = time.time()
    result = {
        "command": command,
        "success": False,
        "execution_time": 0,
        "stdout": "",
        "stderr": ""
    }
    
    try:
        process = subprocess.run(
            command.split(), 
            capture_output=True,
            text=True,
            timeout=timeout
        )
        
        result["success"] = (process.returncode == 0)
        result["execution_time"] = round(time.time() - start_time, 2)
        result["stdout"] = process.stdout
        result["stderr"] = process.stderr
        
        if result["success"]:
            logger.info(f"Succès ({result['execution_time']}s)")
        else:
            logger.warning(f"Échec (code {process.returncode}, {result['execution_time']}s)")
            if process.stderr:
                logger.warning(f"Erreur: {process.stderr.strip()}")
                
    except subprocess.TimeoutExpired:
        logger.error(f"Timeout après {timeout}s: {command}")
        result["stderr"] = f"Timeout après {timeout} secondes"
        result["execution_time"] = timeout
    except Exception as e:
        logger.error(f"Erreur: {str(e)}")
        result["stderr"] = str(e)
        result["execution_time"] = round(time.time() - start_time, 2)
    
    return result

def test_key_kaggle_features():
    """Teste les fonctionnalités essentielles de l'API Kaggle."""
    results = []
    
    # Test de la configuration
    logger.info("=== Test de la configuration ===")
    results.append(run_command("kaggle config view"))
    results.append(run_command("kaggle --version"))
    
    # Test des commandes principales pour les compétitions
    logger.info("=== Test des compétitions ===")
    results.append(run_command("kaggle competitions list -s arc"))
    results.append(run_command("kaggle competitions files arc-prize-2025"))
    results.append(run_command("kaggle competitions download arc-prize-2025 -f sample_submission.json -p ./download_test"))
    
    # Test des commandes principales pour les datasets
    logger.info("=== Test des datasets ===")
    results.append(run_command("kaggle datasets list -s titanic"))
    
    # Test des commandes principales pour les kernels
    logger.info("=== Test des kernels ===")
    results.append(run_command("kaggle kernels list --mine"))
    
    # Générer un rapport
    generate_report(results)
    
    # Résumé
    success_count = sum(1 for r in results if r["success"])
    logger.info(f"Tests terminés: {success_count}/{len(results)} réussis")
    
    return results

def generate_report(results):
    """Génère un rapport à partir des résultats des tests."""
    # Sauvegarder les résultats JSON
    with open(COMMAND_RESULTS_JSON, "w") as f:
        json.dump(results, f, indent=2)
    
    # Créer un rapport texte
    with open(SUMMARY_REPORT, "w") as f:
        f.write("RAPPORT DE TEST RAPIDE DE L'API KAGGLE\n")
        f.write("=" * 80 + "\n\n")
        f.write(f"Généré le: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        
        # Statistiques globales
        total = len(results)
        success = sum(1 for r in results if r["success"])
        
        f.write(f"Tests effectués: {total}\n")
        f.write(f"Tests réussis: {success}\n")
        f.write(f"Tests échoués: {total - success}\n")
        f.write(f"Taux de réussite: {(success/total)*100:.2f}%\n\n")
        
        # Détails des tests
        f.write("DÉTAILS DES TESTS\n")
        f.write("-" * 80 + "\n\n")
        
        for i, result in enumerate(results, 1):
            f.write(f"Test #{i}: {result['command']}\n")
            f.write(f"Statut: {'Réussi' if result['success'] else 'Échoué'}\n")
            f.write(f"Temps d'exécution: {result['execution_time']} secondes\n")
            
            if not result["success"]:
                f.write("Erreur:\n")
                f.write(result["stderr"] + "\n")
            
            f.write("-" * 80 + "\n\n")
    
    logger.info(f"Rapport sauvegardé dans {SUMMARY_REPORT}")

def check_real_time_access():
    """Vérifie l'accès en temps réel à l'API Kaggle."""
    logger.info("Vérification de l'accès en temps réel à l'API Kaggle...")
    
    # 1. Test de connexion
    config_result = run_command("kaggle config view")
    if not config_result["success"]:
        logger.error("Échec de la configuration Kaggle")
        return False
    
    # 2. Test d'accès aux compétitions
    comp_result = run_command("kaggle competitions list -s arc")
    if not comp_result["success"]:
        logger.error("Échec d'accès aux compétitions")
        return False
    
    # 3. Test d'accès aux données ARC Prize 2025
    files_result = run_command("kaggle competitions files arc-prize-2025")
    if not files_result["success"]:
        logger.error("Échec d'accès aux fichiers de la compétition ARC Prize 2025")
        return False
    
    logger.info("Accès en temps réel à l'API Kaggle vérifié avec succès")
    return True

def main():
    """Fonction principale."""
    logger.info("=== TEST RAPIDE DE L'API KAGGLE ===")
    
    # Vérifier l'accès en temps réel
    if not check_real_time_access():
        logger.error("Échec de la vérification d'accès à l'API Kaggle")
        return 1
    
    # Tester les fonctionnalités clés
    test_key_kaggle_features()
    
    logger.info("=== TEST TERMINÉ ===")
    return 0

if __name__ == "__main__":
    sys.exit(main())