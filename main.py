from flask import Flask, render_template, request, redirect, url_for, session, flash
import os
import json
import logging
from analyzer import clone_repo, analyze_repo

# Configuration du logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Création de l'application Flask
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "vorax_secret_key")

@app.route('/')
def index():
    """Page d'accueil avec le formulaire pour cloner le dépôt"""
    return render_template('index.html')

@app.route('/analyze', methods=['POST'])
def analyze():
    """Route pour cloner et analyser le dépôt"""
    if request.method == 'POST':
        repo_url = request.form['repo_url']
        
        # Validation de l'URL du dépôt
        if not repo_url:
            flash("L'URL du dépôt est obligatoire", "error")
            return redirect(url_for('index'))
        
        # Clone le dépôt
        logger.info(f"Clonage du dépôt: {repo_url}")
        try:
            repo_path = clone_repo(repo_url)
            if not repo_path:
                flash("Impossible de cloner le dépôt", "error")
                return redirect(url_for('index'))
            
            # Analyse le dépôt
            logger.info(f"Analyse du dépôt: {repo_path}")
            analysis_result = analyze_repo(repo_path)
            
            # Stocke le résultat dans la session
            session['analysis_result'] = analysis_result
            
            # Redirection vers la page de résultats
            return redirect(url_for('result'))
        except Exception as e:
            logger.error(f"Erreur lors de l'analyse: {str(e)}")
            flash(f"Erreur lors de l'analyse: {str(e)}", "error")
            return redirect(url_for('index'))

@app.route('/result')
def result():
    """Affichage des résultats d'analyse"""
    # Récupération des résultats d'analyse depuis la session
    analysis_result = session.get('analysis_result')
    
    if not analysis_result:
        flash("Aucun résultat d'analyse disponible", "warning")
        return redirect(url_for('index'))
    
    return render_template('result.html', result=analysis_result)

@app.route('/test_arc_api')
def test_arc_api():
    """Exécution du test de l'API ARC et affichage des résultats"""
    try:
        import sys
        import subprocess
        from pathlib import Path
        
        # Chemin vers le script de test
        test_script = Path("vorax_repo/test_arc_api.py")
        
        if not test_script.exists():
            flash("Le script de test ARC n'existe pas", "error")
            return redirect(url_for('index'))
        
        # Exécution du script
        result = subprocess.run(
            [sys.executable, str(test_script)],
            capture_output=True,
            text=True,
            cwd="vorax_repo"
        )
        
        # Récupération du rapport
        report_path = Path("vorax_repo/arc_test/arc_api_report.txt")
        
        if not report_path.exists():
            return render_template('result.html', 
                                 test_output=result.stdout,
                                 test_error=result.stderr,
                                 test_status="Erreur" if result.returncode != 0 else "Succès")
        
        with open(report_path, 'r') as f:
            report_content = f.read()
        
        # Récupération du rapport JSON pour les détails
        json_report_path = Path("vorax_repo/arc_test/arc_api_report.json")
        report_details = None
        
        if json_report_path.exists():
            with open(json_report_path, 'r') as f:
                report_details = json.load(f)
        
        return render_template('result.html', 
                             report=report_content,
                             report_details=report_details,
                             test_output=result.stdout,
                             test_error=result.stderr,
                             test_status="Erreur" if result.returncode != 0 else "Succès")
    
    except Exception as e:
        logger.exception("Erreur lors du test de l'API ARC")
        flash(f"Erreur lors du test de l'API ARC: {str(e)}", "error")
        return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)