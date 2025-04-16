import os
import shutil
import tempfile
import logging
import subprocess
import re
from collections import defaultdict
import glob

def clone_repo(repo_url):
    """
    Clone le dépôt Git dans un répertoire temporaire et retourne le chemin
    """
    logging.debug(f"Clonage du dépôt: {repo_url}")
    temp_dir = tempfile.mkdtemp(prefix="vorax_analysis_")
    
    try:
        # Exécute la commande git clone
        subprocess.run(['git', 'clone', repo_url, temp_dir], 
                       check=True, 
                       capture_output=True)
        
        logging.debug(f"Dépôt cloné avec succès dans: {temp_dir}")
        return temp_dir
    
    except subprocess.CalledProcessError as e:
        # Nettoyage en cas d'erreur
        if os.path.exists(temp_dir):
            shutil.rmtree(temp_dir)
        
        error_msg = f"Erreur lors du clonage: {e.stderr.decode() if e.stderr else str(e)}"
        logging.error(error_msg)
        raise Exception(error_msg)

def analyze_repo(repo_path):
    """
    Analyse le contenu du dépôt et retourne un rapport détaillé
    """
    logging.debug(f"Analyse du dépôt dans: {repo_path}")
    
    result = {
        "completion_percentage": 0,
        "file_stats": {},
        "components": {},
        "git_stats": {},
        "summary": "",
        "recommendations": []
    }
    
    # Analyse des fichiers
    file_stats = analyze_files(repo_path)
    result["file_stats"] = file_stats
    
    # Analyse des composants principaux
    components = analyze_components(repo_path)
    result["components"] = components
    
    # Statistiques Git
    git_stats = analyze_git_history(repo_path)
    result["git_stats"] = git_stats
    
    # Calcul du pourcentage global d'avancement
    completion = calculate_completion(file_stats, components, git_stats)
    result["completion_percentage"] = completion
    
    # Génération du résumé
    result["summary"] = generate_summary(completion, file_stats, components, git_stats)
    
    # Recommandations
    result["recommendations"] = generate_recommendations(components, completion)
    
    # Nettoyage du répertoire temporaire
    logging.debug(f"Nettoyage du répertoire: {repo_path}")
    shutil.rmtree(repo_path)
    
    return result

def analyze_files(repo_path):
    """
    Analyse les statistiques de fichiers dans le dépôt
    """
    stats = {
        "total_files": 0,
        "file_types": defaultdict(int),
        "code_lines": 0,
        "empty_files": 0,
        "large_files": 0,
        "directories": 0
    }
    
    # Parcours des fichiers
    for root, dirs, files in os.walk(repo_path):
        # Exclusion du dossier .git
        if '.git' in dirs:
            dirs.remove('.git')
        
        stats["directories"] += len(dirs)
        
        for file in files:
            file_path = os.path.join(root, file)
            stats["total_files"] += 1
            
            # Extension du fichier
            _, ext = os.path.splitext(file)
            ext = ext.lower()[1:] if ext else "sans_extension"
            stats["file_types"][ext] += 1
            
            # Taille du fichier
            size = os.path.getsize(file_path)
            if size == 0:
                stats["empty_files"] += 1
            if size > 1000000:  # Fichiers > 1MB
                stats["large_files"] += 1
            
            # Comptage des lignes de code pour les fichiers texte
            if ext in ['py', 'js', 'html', 'css', 'c', 'cpp', 'h', 'hpp', 'java', 'php', 'rb', 'txt', 'md', 'sh']:
                try:
                    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                        stats["code_lines"] += sum(1 for line in f if line.strip())
                except Exception as e:
                    logging.warning(f"Impossible de lire le fichier {file_path}: {str(e)}")
    
    return stats

def analyze_components(repo_path):
    """
    Identifie et analyse les composants principaux du projet
    """
    components = {
        "frontend": {
            "exists": False,
            "completion": 0,
            "details": "",
            "files": []
        },
        "backend": {
            "exists": False,
            "completion": 0,
            "details": "",
            "files": []
        },
        "database": {
            "exists": False,
            "completion": 0,
            "details": "",
            "files": []
        },
        "documentation": {
            "exists": False,
            "completion": 0,
            "details": "",
            "files": []
        },
        "tests": {
            "exists": False,
            "completion": 0,
            "details": "",
            "files": []
        }
    }
    
    # Recherche des fichiers frontend
    frontend_files = glob.glob(f"{repo_path}/**/*.html", recursive=True)
    frontend_files += glob.glob(f"{repo_path}/**/*.css", recursive=True)
    frontend_files += glob.glob(f"{repo_path}/**/*.js", recursive=True)
    
    if frontend_files:
        components["frontend"]["exists"] = True
        components["frontend"]["files"] = [os.path.relpath(f, repo_path) for f in frontend_files]
        components["frontend"]["completion"] = estimate_component_completion(frontend_files)
        components["frontend"]["details"] = f"Trouvé {len(frontend_files)} fichiers frontend"
    
    # Recherche des fichiers backend
    backend_files = glob.glob(f"{repo_path}/**/*.py", recursive=True)
    backend_files += glob.glob(f"{repo_path}/**/*.php", recursive=True)
    backend_files += glob.glob(f"{repo_path}/**/*.rb", recursive=True)
    backend_files += glob.glob(f"{repo_path}/**/*.java", recursive=True)
    
    if backend_files:
        components["backend"]["exists"] = True
        components["backend"]["files"] = [os.path.relpath(f, repo_path) for f in backend_files]
        components["backend"]["completion"] = estimate_component_completion(backend_files)
        components["backend"]["details"] = f"Trouvé {len(backend_files)} fichiers backend"
    
    # Recherche des fichiers de base de données
    db_files = glob.glob(f"{repo_path}/**/*.sql", recursive=True)
    db_files += glob.glob(f"{repo_path}/**/*.db", recursive=True)
    db_files += glob.glob(f"{repo_path}/**/*schema*", recursive=True)
    db_files += glob.glob(f"{repo_path}/**/*migration*", recursive=True)
    
    if db_files:
        components["database"]["exists"] = True
        components["database"]["files"] = [os.path.relpath(f, repo_path) for f in db_files]
        components["database"]["completion"] = estimate_component_completion(db_files)
        components["database"]["details"] = f"Trouvé {len(db_files)} fichiers de base de données"
    
    # Recherche des fichiers de documentation
    doc_files = glob.glob(f"{repo_path}/**/*.md", recursive=True)
    doc_files += glob.glob(f"{repo_path}/**/*.rst", recursive=True)
    doc_files += glob.glob(f"{repo_path}/**/*.txt", recursive=True)
    doc_files += glob.glob(f"{repo_path}/**/README*", recursive=True)
    doc_files += glob.glob(f"{repo_path}/**/docs/**", recursive=True)
    
    if doc_files:
        components["documentation"]["exists"] = True
        components["documentation"]["files"] = [os.path.relpath(f, repo_path) for f in doc_files]
        components["documentation"]["completion"] = estimate_component_completion(doc_files)
        components["documentation"]["details"] = f"Trouvé {len(doc_files)} fichiers de documentation"
    
    # Recherche des fichiers de test
    test_files = glob.glob(f"{repo_path}/**/*test*.py", recursive=True)
    test_files += glob.glob(f"{repo_path}/**/*spec*.js", recursive=True)
    test_files += glob.glob(f"{repo_path}/**/tests/**", recursive=True)
    
    if test_files:
        components["tests"]["exists"] = True
        components["tests"]["files"] = [os.path.relpath(f, repo_path) for f in test_files]
        components["tests"]["completion"] = estimate_component_completion(test_files)
        components["tests"]["details"] = f"Trouvé {len(test_files)} fichiers de tests"
    
    return components

def estimate_component_completion(file_list):
    """
    Estime le pourcentage d'achèvement d'un composant en fonction de la taille et du contenu des fichiers
    """
    if not file_list:
        return 0
    
    total_size = 0
    non_empty_files = 0
    
    for file_path in file_list:
        try:
            size = os.path.getsize(file_path)
            total_size += size
            
            if size > 0:
                non_empty_files += 1
        except Exception:
            pass
    
    # Facteurs pour l'estimation
    file_count_factor = min(100, len(file_list) * 5)  # Plus de fichiers = plus complet
    avg_size_factor = min(100, total_size / max(1, len(file_list)) / 100)  # Plus grande taille moyenne = plus complet
    non_empty_ratio = non_empty_files / max(1, len(file_list)) * 100  # Ratio de fichiers non vides
    
    # Moyenne pondérée des facteurs
    completion = (file_count_factor * 0.3) + (avg_size_factor * 0.3) + (non_empty_ratio * 0.4)
    
    return min(100, round(completion))

def analyze_git_history(repo_path):
    """
    Analyse l'historique Git du dépôt
    """
    git_stats = {
        "commit_count": 0,
        "authors": [],
        "first_commit_date": "",
        "last_commit_date": "",
        "branch_count": 0,
        "active_days": 0
    }
    
    try:
        # Nombre de commits
        result = subprocess.run(['git', '-C', repo_path, 'rev-list', '--count', 'HEAD'], 
                               capture_output=True, text=True, check=True)
        git_stats["commit_count"] = int(result.stdout.strip())
        
        # Auteurs
        result = subprocess.run(['git', '-C', repo_path, 'shortlog', '-sne', 'HEAD'], 
                               capture_output=True, text=True, check=True)
        authors = []
        for line in result.stdout.strip().split('\n'):
            if line.strip():
                match = re.search(r'^\s*\d+\s+(.+)\s+<', line)
                if match:
                    authors.append(match.group(1).strip())
        git_stats["authors"] = authors
        
        # Date du premier commit
        result = subprocess.run(['git', '-C', repo_path, 'log', '--reverse', '--format=%cd', '--date=short'], 
                               capture_output=True, text=True, check=True)
        if result.stdout.strip():
            git_stats["first_commit_date"] = result.stdout.strip().split('\n')[0]
        
        # Date du dernier commit
        result = subprocess.run(['git', '-C', repo_path, 'log', '-1', '--format=%cd', '--date=short'], 
                               capture_output=True, text=True, check=True)
        git_stats["last_commit_date"] = result.stdout.strip()
        
        # Nombre de branches
        result = subprocess.run(['git', '-C', repo_path, 'branch', '-a'], 
                               capture_output=True, text=True, check=True)
        git_stats["branch_count"] = len(result.stdout.strip().split('\n'))
        
        # Jours d'activité
        result = subprocess.run(['git', '-C', repo_path, 'log', '--format=%cd', '--date=short'], 
                               capture_output=True, text=True, check=True)
        unique_days = set(result.stdout.strip().split('\n'))
        git_stats["active_days"] = len(unique_days)
        
    except subprocess.CalledProcessError as e:
        logging.error(f"Erreur lors de l'analyse de l'historique Git: {str(e)}")
    
    return git_stats

def calculate_completion(file_stats, components, git_stats):
    """
    Calcule le pourcentage global d'avancement du projet
    """
    # Facteurs de pondération
    component_weights = {
        "frontend": 0.25,
        "backend": 0.3,
        "database": 0.15,
        "documentation": 0.15,
        "tests": 0.15
    }
    
    # Calcul basé sur les composants
    component_score = 0
    component_weight_sum = 0
    
    for component, weight in component_weights.items():
        if components[component]["exists"]:
            component_score += components[component]["completion"] * weight
            component_weight_sum += weight
    
    # Normalisation si tous les composants ne sont pas présents
    component_completion = component_score / max(0.1, component_weight_sum) if component_weight_sum > 0 else 0
    
    # Facteurs supplémentaires
    git_factor = min(100, git_stats.get("commit_count", 0) / 2)  # 200 commits = 100%
    code_lines_factor = min(100, file_stats.get("code_lines", 0) / 100)  # 10,000 lignes = 100%
    
    # Calcul final avec pondération
    completion = (component_completion * 0.6) + (git_factor * 0.2) + (code_lines_factor * 0.2)
    
    return round(completion)

def generate_summary(completion, file_stats, components, git_stats):
    """
    Génère un résumé textuel de l'analyse
    """
    summary = f"Le projet Vorax est actuellement complété à environ {completion}%.\n\n"
    
    # Statistiques générales
    summary += "**Statistiques générales:**\n"
    summary += f"- {file_stats.get('total_files', 0)} fichiers au total\n"
    summary += f"- {file_stats.get('code_lines', 0)} lignes de code\n"
    summary += f"- {file_stats.get('directories', 0)} répertoires\n\n"
    
    # Composants
    summary += "**État des composants:**\n"
    for name, data in components.items():
        if data["exists"]:
            summary += f"- {name.capitalize()}: {data['completion']}% complété ({len(data['files'])} fichiers)\n"
        else:
            summary += f"- {name.capitalize()}: Non trouvé\n"
    
    summary += "\n"
    
    # Activité Git
    summary += "**Historique de développement:**\n"
    if git_stats.get("commit_count", 0) > 0:
        summary += f"- {git_stats.get('commit_count', 0)} commits au total\n"
        summary += f"- {len(git_stats.get('authors', []))} contributeurs\n"
        summary += f"- Premier commit: {git_stats.get('first_commit_date', 'Inconnu')}\n"
        summary += f"- Dernier commit: {git_stats.get('last_commit_date', 'Inconnu')}\n"
        summary += f"- {git_stats.get('active_days', 0)} jours d'activité\n"
    else:
        summary += "- Historique Git non disponible ou vide\n"
    
    return summary

def generate_recommendations(components, completion):
    """
    Génère des recommandations basées sur l'analyse
    """
    recommendations = []
    
    # Recommandations générales basées sur le niveau d'achèvement
    if completion < 25:
        recommendations.append("Le projet semble être dans une phase très préliminaire de développement.")
    elif completion < 50:
        recommendations.append("Le projet est dans une phase de développement précoce.")
    elif completion < 75:
        recommendations.append("Le projet a progressé de manière significative mais nécessite encore du travail.")
    else:
        recommendations.append("Le projet semble être dans une phase avancée de développement.")
    
    # Recommandations spécifiques aux composants
    if not components["documentation"]["exists"] or components["documentation"]["completion"] < 30:
        recommendations.append("La documentation du projet pourrait être améliorée ou créée.")
    
    if not components["tests"]["exists"] or components["tests"]["completion"] < 40:
        recommendations.append("L'ajout de tests automatisés améliorerait la qualité et la maintenabilité du projet.")
    
    if components["frontend"]["exists"] and components["frontend"]["completion"] < 50:
        recommendations.append("L'interface utilisateur nécessite plus de développement.")
    
    if components["backend"]["exists"] and components["backend"]["completion"] < 50:
        recommendations.append("La logique métier du backend nécessite plus de développement.")
    
    if not components["database"]["exists"] and (components["frontend"]["exists"] or components["backend"]["exists"]):
        recommendations.append("Considérer l'ajout d'une persistance des données si le projet en a besoin.")
    
    return recommendations
