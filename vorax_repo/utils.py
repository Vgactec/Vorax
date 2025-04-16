"""
Utility functions for Kaggle API testing.
"""
import os
import sys
import subprocess
import logging
from datetime import datetime
import csv
from pathlib import Path
import config

logger = logging.getLogger(__name__)

def run_command(command, cwd=None, timeout=300, capture_output=True):
    """
    Run a shell command and return its output.
    
    Args:
        command (str or list): Command to run
        cwd (str, optional): Working directory
        timeout (int, optional): Command timeout in seconds
        capture_output (bool, optional): Whether to capture command output
        
    Returns:
        tuple: (returncode, stdout, stderr)
    """
    try:
        logger.info(f"Running command: {command}")
        
        if isinstance(command, str):
            command_list = command.split()
        else:
            command_list = command
            
        result = subprocess.run(
            command_list,
            cwd=cwd,
            timeout=timeout,
            text=True,
            capture_output=capture_output
        )
        
        return result.returncode, result.stdout, result.stderr
    except subprocess.TimeoutExpired:
        logger.error(f"Command timed out after {timeout} seconds: {command}")
        return -1, "", f"Command timed out after {timeout} seconds"
    except Exception as e:
        logger.error(f"Error executing command '{command}': {e}")
        return -1, "", str(e)

def create_kaggle_config(username, api_key):
    """
    Create Kaggle API configuration file.
    
    Args:
        username (str): Kaggle username
        api_key (str): Kaggle API key
        
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        # Create .kaggle directory if it doesn't exist
        kaggle_dir = Path.home() / ".kaggle"
        kaggle_dir.mkdir(exist_ok=True)
        
        # Create kaggle.json file
        kaggle_config = kaggle_dir / "kaggle.json"
        with open(kaggle_config, 'w') as f:
            f.write(f'{{"username":"{username}","key":"{api_key}"}}')
        
        # Set appropriate permissions
        os.chmod(kaggle_config, 0o600)
        
        logger.info(f"Created Kaggle config file at {kaggle_config}")
        return True
    except Exception as e:
        logger.error(f"Error creating Kaggle config: {e}")
        return False

def save_results_to_csv(results):
    """
    Save test results to a CSV file.
    
    Args:
        results (list): List of result dictionaries
        
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        with open(config.COMMAND_RESULTS_CSV, 'w', newline='') as f:
            fieldnames = ['timestamp', 'category', 'command', 'success', 'execution_time', 'output', 'error']
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            for result in results:
                writer.writerow(result)
        logger.info(f"Results saved to {config.COMMAND_RESULTS_CSV}")
        return True
    except Exception as e:
        logger.error(f"Error saving results to CSV: {e}")
        return False

def save_results_to_txt(results):
    """
    Save test results to a text file.
    
    Args:
        results (list): List of result dictionaries
        
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        with open(config.COMMAND_RESULTS_TXT, 'w') as f:
            f.write("KAGGLE API COMMAND TEST RESULTS\n")
            f.write("=" * 80 + "\n\n")
            
            for result in results:
                f.write(f"COMMAND: kaggle {result['category']} {result['command']}\n")
                f.write(f"TIMESTAMP: {result['timestamp']}\n")
                f.write(f"SUCCESS: {result['success']}\n")
                f.write(f"EXECUTION TIME: {result['execution_time']} seconds\n")
                
                f.write("OUTPUT:\n")
                if result['output']:
                    f.write(result['output'] + "\n")
                else:
                    f.write("No output\n")
                
                if result['error']:
                    f.write("ERROR:\n")
                    f.write(result['error'] + "\n")
                    
                f.write("-" * 80 + "\n\n")
        
        logger.info(f"Results saved to {config.COMMAND_RESULTS_TXT}")
        return True
    except Exception as e:
        logger.error(f"Error saving results to text file: {e}")
        return False

def generate_summary_report(results):
    """
    Generate a summary report of all tests.
    
    Args:
        results (list): List of result dictionaries
        
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        total_commands = len(results)
        successful_commands = sum(1 for r in results if r['success'])
        failed_commands = total_commands - successful_commands
        
        with open(config.SUMMARY_REPORT, 'w') as f:
            f.write("KAGGLE API TEST SUMMARY REPORT\n")
            f.write("=" * 80 + "\n\n")
            f.write(f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            
            f.write("SUMMARY STATISTICS\n")
            f.write("-" * 80 + "\n")
            f.write(f"Total commands tested: {total_commands}\n")
            f.write(f"Successful commands: {successful_commands}\n")
            f.write(f"Failed commands: {failed_commands}\n")
            f.write(f"Success rate: {(successful_commands/total_commands)*100:.2f}%\n\n")
            
            f.write("RESULTS BY CATEGORY\n")
            f.write("-" * 80 + "\n")
            
            categories = {}
            for result in results:
                cat = result['category']
                if cat not in categories:
                    categories[cat] = {'total': 0, 'success': 0}
                categories[cat]['total'] += 1
                if result['success']:
                    categories[cat]['success'] += 1
            
            for cat, stats in categories.items():
                success_rate = (stats['success'] / stats['total']) * 100
                f.write(f"Category: {cat}\n")
                f.write(f"  Commands tested: {stats['total']}\n")
                f.write(f"  Successful: {stats['success']}\n")
                f.write(f"  Failed: {stats['total'] - stats['success']}\n")
                f.write(f"  Success rate: {success_rate:.2f}%\n\n")
            
            f.write("FAILED COMMANDS\n")
            f.write("-" * 80 + "\n")
            failed = [r for r in results if not r['success']]
            if failed:
                for result in failed:
                    f.write(f"Command: kaggle {result['category']} {result['command']}\n")
                    f.write(f"Error: {result['error']}\n\n")
            else:
                f.write("No failed commands\n\n")
        
        logger.info(f"Summary report generated at {config.SUMMARY_REPORT}")
        return True
    except Exception as e:
        logger.error(f"Error generating summary report: {e}")
        return False
