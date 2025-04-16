"""
Script pour tester l'API Kaggle spécifiquement pour la compétition ARC Prize 2025.
Ce script se concentre uniquement sur les fonctionnalités nécessaires à la gestion 
et à la soumission des modèles pour ARC Prize 2025.
"""
import os
import sys
import json
import logging
import time
import subprocess
from pathlib import Path
from datetime import datetime

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Constantes
MODEL_REF = "ndarray2000/hybridvoraxmodelv3-arc-prize-2025-ultra-optimis"
COMP_REF = "arc-prize-2025"
WORK_DIR = Path("arc_test")
WORK_DIR.mkdir(exist_ok=True)

def run_command(command, description=None, timeout=60):
    """Exécute une commande shell et retourne son résultat avec un format amélioré."""
    if description:
        logger.info(f"=== {description} ===")
    logger.info(f"Exécution: {command}")
    
    start_time = time.time()
    result = {
        "command": command,
        "description": description,
        "success": False,
        "execution_time": 0,
        "stdout": "",
        "stderr": "",
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
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
            logger.info(f"✅ Succès ({result['execution_time']}s)")
            if process.stdout.strip():
                stdout_lines = process.stdout.strip().split("\n")
                for line in stdout_lines[:5]:  # Limiter à 5 lignes
                    logger.info(f"  {line}")
                if len(stdout_lines) > 5:
                    logger.info(f"  ... {len(stdout_lines) - 5} lignes supplémentaires")
        else:
            logger.error(f"❌ Échec (code {process.returncode}, {result['execution_time']}s)")
            if process.stderr.strip():
                logger.error(f"  Erreur: {process.stderr.strip()}")
                
    except subprocess.TimeoutExpired:
        logger.error(f"⏱️ Timeout après {timeout}s: {command}")
        result["stderr"] = f"Timeout après {timeout} secondes"
        result["execution_time"] = timeout
    except Exception as e:
        logger.error(f"⚠️ Erreur: {str(e)}")
        result["stderr"] = str(e)
        result["execution_time"] = round(time.time() - start_time, 2)
    
    logger.info("-" * 80)
    return result

def verify_kaggle_api():
    """Vérifie que l'API Kaggle est correctement configurée."""
    logger.info("Vérification de la configuration de l'API Kaggle")
    
    # Test de la configuration
    config_result = run_command(
        "kaggle config view", 
        "Vérification de la configuration Kaggle"
    )
    
    if not config_result["success"]:
        logger.error("La configuration Kaggle n'est pas valide")
        return False
    
    # Vérifier que l'utilisateur est connecté
    if "username" not in config_result["stdout"]:
        logger.error("L'utilisateur n'est pas connecté à Kaggle")
        return False
    
    logger.info("API Kaggle correctement configurée")
    return True

def test_arc_competition_access():
    """Teste l'accès à la compétition ARC Prize 2025."""
    results = []
    
    # Liste des compétitions ARC
    results.append(run_command(
        "kaggle competitions list -s arc",
        "Liste des compétitions ARC"
    ))
    
    # Fichiers de la compétition
    results.append(run_command(
        f"kaggle competitions files {COMP_REF}",
        "Fichiers de la compétition ARC Prize 2025"
    ))
    
    # Téléchargement d'un fichier d'exemple
    results.append(run_command(
        f"kaggle competitions download {COMP_REF} -f sample_submission.json -p {WORK_DIR}",
        "Téléchargement du fichier d'exemple de soumission"
    ))
    
    # Vérification du fichier téléchargé
    submission_file = WORK_DIR / "sample_submission.json"
    if submission_file.exists():
        logger.info(f"✅ Fichier d'exemple téléchargé: {submission_file} ({submission_file.stat().st_size} octets)")
        
        # Vérifier le contenu du fichier JSON
        try:
            with open(submission_file, 'r') as f:
                sample_data = json.load(f)
            logger.info(f"✅ Format JSON valide, {len(sample_data)} entrées")
        except json.JSONDecodeError:
            logger.error("❌ Format JSON invalide")
    else:
        logger.error(f"❌ Fichier d'exemple non téléchargé: {submission_file}")
    
    # Liste des soumissions
    results.append(run_command(
        f"kaggle competitions submissions {COMP_REF}",
        "Liste des soumissions pour ARC Prize 2025"
    ))
    
    # Classement
    results.append(run_command(
        f"kaggle competitions leaderboard {COMP_REF} --show",
        "Classement de la compétition ARC Prize 2025"
    ))
    
    return results

def test_arc_model_operations():
    """Teste les opérations sur le modèle HybridVorax pour ARC Prize 2025."""
    results = []
    
    # Liste des kernels
    results.append(run_command(
        "kaggle kernels list --mine",
        "Liste de mes kernels Kaggle"
    ))
    
    # Informations sur le modèle
    results.append(run_command(
        f"kaggle kernels status {MODEL_REF}",
        "Statut du modèle HybridVorax"
    ))
    
    # Téléchargement du modèle
    results.append(run_command(
        f"kaggle kernels pull {MODEL_REF} -p {WORK_DIR}/model",
        "Téléchargement du modèle HybridVorax"
    ))
    
    # Vérifier que le notebook a été téléchargé
    model_file = WORK_DIR / "model" / f"{MODEL_REF.split('/')[-1]}.ipynb"
    if model_file.exists():
        logger.info(f"✅ Notebook téléchargé: {model_file} ({model_file.stat().st_size} octets)")
        
        # Afficher les premières lignes du notebook
        try:
            with open(model_file, 'r') as f:
                notebook_data = json.load(f)
            
            cell_count = len(notebook_data.get("cells", []))
            metadata = notebook_data.get("metadata", {})
            kernelspec = metadata.get("kernelspec", {})
            language = kernelspec.get("language", "unknown")
            
            logger.info(f"✅ Notebook valide: {cell_count} cellules, langage {language}")
        except json.JSONDecodeError:
            logger.error("❌ Format de notebook invalide")
    else:
        logger.error(f"❌ Notebook non téléchargé: {model_file}")
    
    # On ne teste pas le push pour éviter de modifier le kernel
    logger.info("⚠️ Test de 'push' ignoré pour éviter de modifier le kernel existant")
    
    return results

def create_report(competition_results, model_results):
    """Crée un rapport détaillé sur les tests."""
    all_results = competition_results + model_results
    success_count = sum(1 for r in all_results if r["success"])
    total_count = len(all_results)
    
    report = {
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "summary": {
            "total_tests": total_count,
            "successful_tests": success_count,
            "failed_tests": total_count - success_count,
            "success_rate": round((success_count / total_count) * 100, 2) if total_count > 0 else 0
        },
        "tests": {
            "competition": competition_results,
            "model": model_results
        }
    }
    
    # Sauvegarder le rapport
    report_file = WORK_DIR / "arc_api_report.json"
    with open(report_file, 'w') as f:
        json.dump(report, f, indent=2)
    
    # Générer un rapport texte
    report_text = WORK_DIR / "arc_api_report.txt"
    with open(report_text, 'w') as f:
        f.write("RAPPORT DE TEST DE L'API KAGGLE POUR ARC PRIZE 2025\n")
        f.write("=" * 80 + "\n\n")
        f.write(f"Date: {report['timestamp']}\n\n")
        
        f.write("RÉSUMÉ\n")
        f.write("-" * 80 + "\n")
        f.write(f"Tests réalisés: {report['summary']['total_tests']}\n")
        f.write(f"Tests réussis: {report['summary']['successful_tests']}\n")
        f.write(f"Tests échoués: {report['summary']['failed_tests']}\n")
        f.write(f"Taux de réussite: {report['summary']['success_rate']}%\n\n")
        
        f.write("TESTS DE LA COMPÉTITION\n")
        f.write("-" * 80 + "\n")
        for result in competition_results:
            f.write(f"Test: {result['description']}\n")
            f.write(f"Commande: {result['command']}\n")
            f.write(f"Résultat: {'Réussi' if result['success'] else 'Échec'}\n")
            f.write(f"Temps: {result['execution_time']} secondes\n")
            if not result['success'] and result['stderr']:
                f.write(f"Erreur: {result['stderr']}\n")
            f.write("\n")
        
        f.write("TESTS DU MODÈLE\n")
        f.write("-" * 80 + "\n")
        for result in model_results:
            f.write(f"Test: {result['description']}\n")
            f.write(f"Commande: {result['command']}\n")
            f.write(f"Résultat: {'Réussi' if result['success'] else 'Échec'}\n")
            f.write(f"Temps: {result['execution_time']} secondes\n")
            if not result['success'] and result['stderr']:
                f.write(f"Erreur: {result['stderr']}\n")
            f.write("\n")
        
        f.write("RECOMMANDATIONS\n")
        f.write("-" * 80 + "\n")
        if report['summary']['success_rate'] == 100:
            f.write("✅ L'API Kaggle fonctionne parfaitement pour ARC Prize 2025.\n")
            f.write("Vous pouvez continuer à utiliser le modèle HybridVorax sans problème.\n")
        elif report['summary']['success_rate'] >= 80:
            f.write("⚠️ L'API Kaggle fonctionne avec quelques limitations pour ARC Prize 2025.\n")
            f.write("Vérifiez les erreurs spécifiques et essayez de les corriger.\n")
        else:
            f.write("❌ L'API Kaggle rencontre des problèmes importants pour ARC Prize 2025.\n")
            f.write("Vérifiez votre connexion et la configuration de l'API.\n")
    
    logger.info(f"Rapport sauvegardé dans {report_file} et {report_text}")
    return report

def main():
    """Fonction principale pour tester l'API Kaggle pour ARC Prize 2025."""
    logger.info("=" * 80)
    logger.info("TEST DE L'API KAGGLE POUR ARC PRIZE 2025")
    logger.info("=" * 80)
    
    # Vérifier l'API Kaggle
    if not verify_kaggle_api():
        logger.error("Configuration de l'API Kaggle invalide. Arrêt des tests.")
        return 1
    
    # Tester l'accès à la compétition
    logger.info("\n\nTEST D'ACCÈS À LA COMPÉTITION ARC PRIZE 2025")
    logger.info("=" * 80)
    competition_results = test_arc_competition_access()
    
    # Tester les opérations sur le modèle
    logger.info("\n\nTEST DES OPÉRATIONS SUR LE MODÈLE HYBRIDVORAX")
    logger.info("=" * 80)
    model_results = test_arc_model_operations()
    
    # Créer un rapport
    logger.info("\n\nGÉNÉRATION DU RAPPORT")
    logger.info("=" * 80)
    report = create_report(competition_results, model_results)
    
    # Afficher le résumé
    logger.info("\n\nRÉSUMÉ")
    logger.info("=" * 80)
    logger.info(f"Tests réalisés: {report['summary']['total_tests']}")
    logger.info(f"Tests réussis: {report['summary']['successful_tests']}")
    logger.info(f"Tests échoués: {report['summary']['failed_tests']}")
    logger.info(f"Taux de réussite: {report['summary']['success_rate']}%")
    
    logger.info("\nTEST TERMINÉ")
    
    return 0 if report['summary']['success_rate'] > 80 else 1

if __name__ == "__main__":
    sys.exit(main())