"""
Runner Script for PDF Scraper Pipeline
--------------------------------------
This script controls the execution flow for setting up or updating a PDF-based document
database and vector store. The behavior is determined by the settings
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
    pdf_down_mode = config["preprocess"]["download_mode"].upper()
    base_url = config["preprocess"]["download_site"]

    # Define base directory for the script
    BASE_DIR = Path().cwd()
    PDF_PROC_DIR = BASE_DIR / "statschat" / "pdf_processing"
    EMBEDDING_DIR = BASE_DIR / "statschat" / "embedding"

    print(f"Pipeline mode: {pdf_down_mode}\n")
    print(f"Executing full {pdf_down_mode} pipeline...\n")

    # Step 1: Download PDFs
    if base_url == "":
        print("No base URL provided, using local PDFs.")
        run_script(PDF_PROC_DIR / "pdf_local_load.py")
    else:
        print(f"PDF site: {base_url}")
        run_script(PDF_PROC_DIR / "pdf_downloader.py")
    # Step 2: Convert PDFs to JSON
    run_script(PDF_PROC_DIR / "pdf_to_json.py")
    # Step 3: Preprocess JSONs and populate vector store
    run_script(EMBEDDING_DIR / "preprocess.py")
    # Step 2: Execute pipeline based on mode
    if pdf_down_mode == "UPDATE":
        run_script(PDF_PROC_DIR / "merge_database_files.py")
    elif pdf_down_mode == "SETUP":
        pass

    else:
        raise ValueError(f"Invalid pdf_files_mode in configuration: '{pdf_down_mode}'")
