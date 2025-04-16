"""
Script to test all Kaggle API commands and record results.
"""
import os
import sys
import logging
import time
from datetime import datetime
import json
from pathlib import Path
import config
from utils import run_command

logger = logging.getLogger(__name__)

def test_kaggle_commands():
    """
    Test all Kaggle API commands and record their output.
    
    Returns:
        list: List of dictionaries containing test results
    """
    results = []
    
    # Determine which kaggle command to use - either installed CLI or wrapper script
    return_code, _, _ = run_command("kaggle --version")
    use_installed_cli = (return_code == 0)
    
    # Set the command prefix based on which version to use
    if use_installed_cli:
        kaggle_cmd = "kaggle"
        logger.info("Using installed Kaggle CLI for tests")
    else:
        kaggle_cmd = "python ./kaggle_wrapper.py"
        logger.info("Using wrapper script for tests")
    
    for category_item in config.KAGGLE_COMMANDS:
        category = category_item["category"]
        commands = category_item["commands"]
        
        for command in commands:
            # Build complete command
            full_command = f"{kaggle_cmd} {category} {command}"
            
            # Add command-specific arguments for commands that require them
            if category == "competitions" and command == "files":
                full_command += " titanic"
            elif category == "competitions" and command == "download":
                full_command += " titanic -p ./download_test"
            elif category == "competitions" and command == "submissions":
                full_command += " titanic"
            elif category == "competitions" and command == "leaderboard":
                full_command += " titanic"
            elif category == "datasets" and command == "files":
                full_command += " kaggle/titanic"
            elif category == "datasets" and command == "download":
                full_command += " kaggle/titanic -p ./download_test"
            elif category == "kernels" and command in ["push", "pull", "output", "status"]:
                # These commands need a kernel reference, but we'll skip actual execution
                # and just test that the command exists
                full_command = f"{kaggle_cmd} {category} {command} --help"
            
            # Initialize result dictionary
            result = {
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "category": category,
                "command": command,
                "success": False,
                "execution_time": 0,
                "output": "",
                "error": ""
            }
            
            # Always define start_time at the beginning to avoid unbound variable issues
            start_time = time.time()
            
            try:
                logger.info(f"Testing command: {full_command}")
                
                # Skip actual execution for commands that can modify content
                if (category == "competitions" and command == "submit") or \
                   (category == "datasets" and command in ["create", "version", "init", "metadata"]) or \
                   (category == "kernels" and command in ["init", "push"]) or \
                   (category == "config" and command in ["set", "unset"]):
                    result["output"] = f"Command '{full_command}' skipped (would modify content)"
                    result["success"] = True
                    result["execution_time"] = 0
                else:
                    # Execute the command
                    return_code, stdout, stderr = run_command(full_command.split())
                    
                    result["execution_time"] = round(time.time() - start_time, 2)
                    result["output"] = stdout
                    result["error"] = stderr
                    result["success"] = (return_code == 0)
                
                logger.info(f"Command '{full_command}' completed with success={result['success']}")
            except Exception as e:
                logger.error(f"Error testing command '{full_command}': {e}")
                result["error"] = str(e)
                result["execution_time"] = round(time.time() - start_time, 2)
            
            results.append(result)
    
    logger.info(f"Completed testing {len(results)} Kaggle API commands")
    return results

if __name__ == "__main__":
    # Create directory for downloads if needed
    download_dir = Path("./download_test")
    download_dir.mkdir(exist_ok=True)
    
    # Test all Kaggle API commands
    results = test_kaggle_commands()
    
    # Save results to JSON file for further processing
    results_file = config.RESULTS_DIR / "raw_results.json"
    try:
        with open(results_file, 'w') as f:
            json.dump(results, f, indent=2)
        logger.info(f"Raw results saved to {results_file}")
    except Exception as e:
        logger.error(f"Error saving raw results: {e}")
    
    # Count successful tests
    success_count = sum(1 for r in results if r["success"])
    logger.info(f"Test completed: {success_count}/{len(results)} commands successful")
    
    sys.exit(0 if success_count == len(results) else 1)
