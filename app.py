import os
import logging
from flask import Flask, render_template, request, flash, redirect, url_for, session
from analyzer import clone_repo, analyze_repo

# Configuration du logging
logging.basicConfig(level=logging.DEBUG)

# Création de l'application Flask
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "vorax_analysis_secret_key")

# Routes
@app.route('/', methods=['GET'])
def index():
    """Page d'accueil avec le formulaire pour cloner le dépôt"""
    return render_template('index.html')

@app.route('/analyze', methods=['POST'])
def analyze():
    """Route pour cloner et analyser le dépôt"""
    repo_url = request.form.get('repo_url', '').strip()
    
    # Validation de l'URL
    if not repo_url:
        flash("L'URL du dépôt est requise", "error")
        return redirect(url_for('index'))
    
    # Vérification que l'URL est bien celle du projet Vorax
    if "github.com/Vgactec/Vorax" not in repo_url:
        flash("Cette application est conçue uniquement pour analyser le projet Vorax", "error")
        return redirect(url_for('index'))
    
    try:
        # Clonage du dépôt
        repo_path = clone_repo(repo_url)
        
        # Analyse du dépôt
        analysis_result = analyze_repo(repo_path)
        
        # Stockage des résultats dans la session
        session['analysis_result'] = analysis_result
        
        return redirect(url_for('result'))
    
    except Exception as e:
        logging.error(f"Erreur lors de l'analyse: {str(e)}")
        flash(f"Une erreur s'est produite lors de l'analyse: {str(e)}", "error")
        return redirect(url_for('index'))

@app.route('/result', methods=['GET'])
def result():
    """Affichage des résultats d'analyse"""
    analysis_result = session.get('analysis_result')
    
    if not analysis_result:
        flash("Aucun résultat d'analyse disponible", "error")
        return redirect(url_for('index'))
    
    return render_template('result.html', result=analysis_result)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
