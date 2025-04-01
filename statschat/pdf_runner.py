"""
Runner Script for PDF Scraper Pipeline
--------------------------------------
This script controls the execution flow for setting up or updating a PDF-based document
database and vector store. The behavior is determined by the 'pdf_files_mode' setting
in the main TOML configuration file.

Execution Flow:
- SETUP:
    1. Download all PDFs
    2. Convert PDFs to JSON
    3. Preprocess JSONs and populate the vector store from scratch

- UPDATE:
    1. Download new PDFs only
    2. Convert only new PDFs to JSON
    3. Update the vector store with new data

Each step is modular and run as an independent subprocess.
"""

import subprocess
import sys
from statschat import load_config
from pathlib import Path


def run_script(script_name: str):
    """
    Runs a Python script in a subprocess and streams its output.

    Parameters
    ----------
    script_name : str
        The path to the Python script to execute.

    Raises
    ------
    subprocess.CalledProcessError
        If the subprocess exits with a non-zero status.
    """
    print(f"Running script: {script_name}")
    try:
        subprocess.run([sys.executable, script_name], check=True)
        print(f"Finished: {script_name}\n")
    except subprocess.CalledProcessError as e:
        print(f"Error occurred while running {script_name} (Exit Code: {e.returncode})")
        raise


if __name__ == "__main__":
    print("Starting pdf_runner.py...")

    # Load configuration
    config = load_config(name="main")
    pdf_mode = config["runner"]["pdf_files_mode"].upper()

    # Define base directory for the script
    BASE_DIR = Path().cwd()
    PDF_PROC_DIR = BASE_DIR / "statschat" / "pdf_processing"
    EMBEDDING_DIR = BASE_DIR / "statschat" / "embedding"

    print(f"Pipeline mode: {pdf_mode}\n")

    # Step 1: Download PDFs
    run_script(PDF_PROC_DIR / "pdf_downloader.py")

    # Step 2: Execute pipeline based on mode
    if pdf_mode == "SETUP":
        print("Executing full setup pipeline...")
        run_script(PDF_PROC_DIR / "pdf_to_json.py")
        run_script(EMBEDDING_DIR / "preprocess.py")

    elif pdf_mode == "UPDATE":
        print("Executing update pipeline...")
        run_script(PDF_PROC_DIR / "pdf_database_update.py")
        run_script(EMBEDDING_DIR / "preprocess_update_db.py")
        run_script(PDF_PROC_DIR / "merge_database_files.py")

    else:
        raise ValueError(f"Invalid pdf_files_mode in configuration: '{pdf_mode}'")
