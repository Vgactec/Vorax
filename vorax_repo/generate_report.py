"""
Script to generate reports from the Kaggle API test results.
"""
import os
import sys
import logging
import json
from pathlib import Path
import config
from utils import save_results_to_csv, save_results_to_txt, generate_summary_report

logger = logging.getLogger(__name__)

def generate_reports():
    """
    Generate CSV, TXT, and summary reports from test results.
    
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        # Load raw results
        raw_results_file = config.RESULTS_DIR / "raw_results.json"
        
        if not raw_results_file.exists():
            logger.error(f"Raw results file not found at {raw_results_file}")
            return False
        
        with open(raw_results_file, 'r') as f:
            results = json.load(f)
        
        logger.info(f"Loaded {len(results)} test results from {raw_results_file}")
        
        # Generate CSV report
        if not save_results_to_csv(results):
            logger.error("Failed to generate CSV report")
            return False
        
        # Generate TXT report
        if not save_results_to_txt(results):
            logger.error("Failed to generate TXT report")
            return False
        
        # Generate summary report
        if not generate_summary_report(results):
            logger.error("Failed to generate summary report")
            return False
        
        logger.info("All reports generated successfully")
        return True
    except Exception as e:
        logger.error(f"Error generating reports: {e}")
        return False

if __name__ == "__main__":
    if not generate_reports():
        logger.error("Failed to generate reports")
        sys.exit(1)
    
    logger.info("Report generation completed successfully")
    sys.exit(0)
