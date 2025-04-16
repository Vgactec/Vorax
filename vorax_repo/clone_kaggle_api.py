"""
Script to clone the Kaggle API repository from GitHub.
"""
import os
import sys
import logging
import git
from pathlib import Path
import config
from utils import run_command

logger = logging.getLogger(__name__)

def clone_kaggle_api():
    """
    Clone the Kaggle API repository from GitHub.
    
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        # Check if repository already exists
        kaggle_repo_dir = config.KAGGLE_REPO_DIR
        if kaggle_repo_dir.exists():
            logger.info(f"Repository already exists at {kaggle_repo_dir}")
            return True
        
        logger.info(f"Cloning Kaggle API repository from {config.KAGGLE_REPO_URL}")
        
        # Create parent directory if it doesn't exist
        kaggle_repo_dir.parent.mkdir(exist_ok=True)
        
        # Clone the repository
        git.Repo.clone_from(config.KAGGLE_REPO_URL, kaggle_repo_dir)
        
        logger.info(f"Repository cloned successfully to {kaggle_repo_dir}")
        return True
    except git.GitCommandError as e:
        logger.error(f"Git error while cloning repository: {e}")
        return False
    except Exception as e:
        logger.error(f"Error cloning repository: {e}")
        return False

def fallback_clone_with_subprocess():
    """
    Alternative method to clone the repository using subprocess.
    
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        logger.info("Attempting to clone repository using subprocess")
        kaggle_repo_dir = config.KAGGLE_REPO_DIR
        
        if kaggle_repo_dir.exists():
            logger.info(f"Repository already exists at {kaggle_repo_dir}")
            return True
            
        # Create parent directory if it doesn't exist
        kaggle_repo_dir.parent.mkdir(exist_ok=True)
        
        command = f"git clone {config.KAGGLE_REPO_URL} {kaggle_repo_dir}"
        return_code, stdout, stderr = run_command(command)
        
        if return_code == 0:
            logger.info(f"Repository cloned successfully to {kaggle_repo_dir}")
            return True
        else:
            logger.error(f"Failed to clone repository: {stderr}")
            return False
    except Exception as e:
        logger.error(f"Error in fallback clone: {e}")
        return False

if __name__ == "__main__":
    if not clone_kaggle_api():
        logger.warning("Primary clone method failed, trying fallback method")
        if not fallback_clone_with_subprocess():
            logger.error("Failed to clone Kaggle API repository")
            sys.exit(1)
        
    logger.info("Repository cloning completed successfully")
    sys.exit(0)
