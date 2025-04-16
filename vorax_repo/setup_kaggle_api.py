"""
Script to set up the Kaggle API by installing dependencies and configuring credentials.
"""
import os
import sys
import logging
from pathlib import Path
import config
from utils import run_command, create_kaggle_config

logger = logging.getLogger(__name__)

def install_dependencies():
    """
    Install the required dependencies for the Kaggle API.
    
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        logger.info("Setting up Kaggle API dependencies")
        
        # Since we've installed Kaggle via packager_tool, we can just verify it works
        return_code, stdout, stderr = run_command("kaggle --version")
        
        if return_code != 0:
            logger.error(f"Failed to verify Kaggle installation: {stderr}")
            logger.info("Using repository instead")
            
            # Navigate to the Kaggle API directory
            kaggle_repo_dir = config.KAGGLE_REPO_DIR
            if not kaggle_repo_dir.exists():
                logger.error(f"Kaggle API repository not found at {kaggle_repo_dir}")
                return False
            
            # Instead of installing in development mode, we add the kaggle-api directory to sys.path
            # so that the script can import the kaggle module
            import sys
            kaggle_cli_path = str(kaggle_repo_dir)
            if kaggle_cli_path not in sys.path:
                sys.path.insert(0, kaggle_cli_path)
                logger.info(f"Added {kaggle_cli_path} to Python path")
            
            # Create a simple wrapper script for kaggle command
            kaggle_script = Path("./kaggle_wrapper.py")
            with open(kaggle_script, 'w') as f:
                f.write("""#!/usr/bin/env python
import sys
import os
from pathlib import Path

# Add the kaggle-api directory to the Python path
kaggle_api_dir = Path.cwd() / "kaggle-api"
sys.path.insert(0, str(kaggle_api_dir))

# Import the kaggle module and run the CLI
from kaggle.cli import main
main()
""")
            os.chmod(kaggle_script, 0o755)
            logger.info(f"Created Kaggle wrapper script at {kaggle_script}")
            
            # Verify the script can be run
            return_code, stdout, stderr = run_command(
                f"python {kaggle_script} --version"
            )
            
            if return_code != 0:
                logger.error(f"Failed to verify Kaggle CLI wrapper: {stderr}")
                return False
        else:
            logger.info(f"Using installed Kaggle package: {stdout.strip()}")
        
        logger.info("Kaggle API dependencies set up successfully")
        return True
    except Exception as e:
        logger.error(f"Error setting up dependencies: {e}")
        return False

def setup_kaggle_api():
    """
    Set up the Kaggle API with the provided credentials.
    
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        # Get Kaggle credentials
        username, api_key = config.get_kaggle_credentials()
        
        if not username or not api_key:
            logger.error("Invalid Kaggle credentials")
            return False
        
        logger.info(f"Setting up Kaggle API for user: {username}")
        
        # Create Kaggle configuration file
        if not create_kaggle_config(username, api_key):
            logger.error("Failed to create Kaggle configuration file")
            return False
        
        # Verify configuration using the installed Kaggle CLI or our wrapper script
        # First try the installed CLI
        return_code, stdout, stderr = run_command("kaggle config view")
        
        if return_code != 0:
            logger.warning(f"Failed to verify with installed Kaggle CLI: {stderr}")
            logger.info("Trying wrapper script instead")
            
            # Try the wrapper script if it exists
            kaggle_script = Path("./kaggle_wrapper.py")
            if kaggle_script.exists():
                return_code, stdout, stderr = run_command("python ./kaggle_wrapper.py config view")
                if return_code != 0:
                    logger.error(f"Failed to verify Kaggle configuration: {stderr}")
                    return False
            else:
                logger.error("No way to verify Kaggle configuration")
                return False
        
        logger.info("Kaggle API configured successfully")
        return True
    except Exception as e:
        logger.error(f"Error setting up Kaggle API: {e}")
        return False

if __name__ == "__main__":
    # Install dependencies
    if not install_dependencies():
        logger.error("Failed to install dependencies")
        sys.exit(1)
    
    # Setup Kaggle API with credentials
    if not setup_kaggle_api():
        logger.error("Failed to set up Kaggle API")
        sys.exit(1)
    
    logger.info("Kaggle API setup completed successfully")
    sys.exit(0)
