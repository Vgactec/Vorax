"""
Configuration file for Kaggle API testing scripts.
"""
import os
import json
import logging
from pathlib import Path

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("kaggle_api_test.log"),
        logging.StreamHandler()
    ]
)

# Paths
BASE_DIR = Path.cwd()
KAGGLE_REPO_DIR = BASE_DIR / "kaggle-api"
RESULTS_DIR = BASE_DIR / "results"
RESULTS_DIR.mkdir(exist_ok=True)

# Kaggle API GitHub repository
KAGGLE_REPO_URL = "https://github.com/Kaggle/kaggle-api.git"

# Extract credentials from the provided JSON file
def get_kaggle_credentials():
    try:
        creds_file = BASE_DIR / "attached_assets" / "kaggle 4.json"
        if creds_file.exists():
            with open(creds_file, 'r') as f:
                credentials = json.load(f)
                return credentials.get("username"), credentials.get("key")
        else:
            logging.error(f"Credentials file not found at {creds_file}")
            return None, None
    except Exception as e:
        logging.error(f"Error reading credentials: {e}")
        return None, None

# Kaggle API commands to test
KAGGLE_COMMANDS = [
    {"category": "competitions", "commands": [
        "list", "files", "download", "submit", "submissions", "leaderboard"
    ]},
    {"category": "datasets", "commands": [
        "list", "files", "download", "create", "version", "init", "metadata"
    ]},
    {"category": "kernels", "commands": [
        "list", "init", "push", "pull", "output", "status"
    ]},
    {"category": "config", "commands": [
        "view", "set", "unset"
    ]},
    {"category": "models", "commands": [
        "list", "instances"
    ]}
]

# Output file paths
COMMAND_RESULTS_CSV = RESULTS_DIR / "kaggle_api_test_results.csv"
COMMAND_RESULTS_TXT = RESULTS_DIR / "kaggle_api_test_results.txt"
SUMMARY_REPORT = RESULTS_DIR / "summary_report.txt"
