#!/usr/bin/env python3
"""
TakoApp Environment Setup Script (Windows Only)
This script automates the setup of the TakoApp environment for Windows users, including:
- Python virtual environment
- Dependencies installation
- MySQL installation and configuration
- Ollama installation and model setup
"""

import os
import sys
import subprocess
import time
import requests
from pathlib import Path
import mysql.connector
from mysql.connector import Error
import webbrowser

from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

DB_USER = os.getenv("DB_USER") or os.getenv("DATABASE_USER") or os.getenv("MYSQL_USER") or "root"
DB_PASSWORD = os.getenv("DB_PASSWORD") or os.getenv("DATABASE_PASSWORD") or os.getenv("MYSQL_PASSWORD")
DB_HOST = os.getenv("DB_HOST") or os.getenv("DATABASE_HOST") or "localhost"
DB_NAME = os.getenv("DB_NAME") or os.getenv("DATABASE_NAME") or "takoapp"

def print_step(message):
    """Print a formatted step message."""
    print(f"\n{'='*80}\n{message}\n{'='*80}")

def run_command(command, shell=False):
    """Run a command and return its output."""
    try:
        if shell:
            process = subprocess.run(command, shell=True, check=True, text=True, capture_output=True)
        else:
            process = subprocess.run(command, check=True, text=True, capture_output=True)
        return process.stdout
    except subprocess.CalledProcessError as e:
        print(f"Error executing command: {e}")
        print(f"Error output: {e.stderr}")
        sys.exit(1)

def check_python_version():
    """Check if Python version is compatible."""
    print_step("Checking Python version...")
    required_version = (3, 10, 16)
    current_version = sys.version_info
    if current_version < required_version:
        print(f"Error: Python {required_version[0]}.{required_version[1]}.{required_version[2]} is required")
        print(f"Current version: {current_version[0]}.{current_version[1]}.{current_version[2]}")
        sys.exit(1)
    print(f"Python version {current_version[0]}.{current_version[1]}.{current_version[2]} detected")

def create_virtual_environment():
    """Create and activate virtual environment."""
    print_step("Setting up Python virtual environment...")
    venv_path = Path("venv")
    if not venv_path.exists():
        run_command([sys.executable, "-m", "venv", "venv"])
    print("Virtual environment created successfully")

def install_dependencies():
    """Install required Python packages."""
    print_step("Installing Python dependencies...")
    pip_cmd = ["./venv/Scripts/pip"]
    run_command(pip_cmd + ["install", "--upgrade", "pip"])
    run_command(pip_cmd + ["install", "-r", "requirements.txt"])
    print("Dependencies installed successfully")

def setup_mysql():
    """Install and configure MySQL and MySQL Workbench (Windows only)."""
    print_step("Setting up MySQL and MySQL Workbench (Windows)...")
    print("Please download and install MySQL from: https://dev.mysql.com/downloads/installer/")
    webbrowser.open("https://dev.mysql.com/downloads/installer/")
    input("Press Enter after installing MySQL...")
    print("Please download and install MySQL Workbench from: https://dev.mysql.com/downloads/workbench/")
    webbrowser.open("https://dev.mysql.com/downloads/workbench/")
    input("Press Enter after installing MySQL Workbench...")
    # Start MySQL service
    run_command("net start MySQL80", shell=True)
    print("MySQL setup completed")

def create_database():
    """Create the application database."""
    print_step("Creating application database...")
    try:
        connection = mysql.connector.connect(
            host=DB_HOST,
            user=DB_USER,
            password=DB_PASSWORD
        )
        cursor = connection.cursor()
        cursor.execute(f"CREATE DATABASE IF NOT EXISTS {DB_NAME}")
        print("Database created successfully")
    except Error as e:
        print(f"Error creating database: {e}")
        sys.exit(1)
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

def setup_ollama():
    """Install and configure Ollama (Windows only)."""
    print_step("Setting up Ollama (Windows)...")
    print("Please download and install Ollama from: https://ollama.ai/download")
    webbrowser.open("https://ollama.ai/download")
    input("Press Enter after installing Ollama...")
    # Start Ollama service
    run_command("start ollama", shell=True)
    print("Waiting for Ollama to start...")
    time.sleep(5)
    print("Pulling llama2 model...")
    run_command("ollama pull llama2", shell=True)
    print("Ollama setup completed")

def verify_setup():
    """Verify the setup by running basic checks."""
    print_step("Verifying setup...")
    # Check database connection
    try:
        connection = mysql.connector.connect(
            host=DB_HOST,
            user=DB_USER,
            password=DB_PASSWORD,
            database=DB_NAME
        )
        print("✅ Database connection successful")
        connection.close()
    except Error as e:
        print(f"❌ Database connection failed: {e}")
    # Check Ollama
    try:
        response = requests.get("http://localhost:11434/api/tags")
        if response.status_code == 200:
            print("✅ Ollama is running")
            models = response.json().get("models", [])
            if any(model["name"] == "llama2" for model in models):
                print("✅ llama2 model is available")
            else:
                print("❌ llama2 model is not available")
        else:
            print("❌ Ollama is not running")
    except requests.exceptions.ConnectionError:
        print("❌ Ollama is not running")

def main():
    print("Starting TakoApp environment setup (Windows only)...")
    check_python_version()
    create_virtual_environment()
    install_dependencies()
    setup_mysql()
    create_database()
    setup_ollama()
    verify_setup()
    print_step("Setup completed successfully!")
    print("""
Next steps:
1. Activate the virtual environment:
   .\\venv\\Scripts\\activate
2. Start the application:
   python run.py
3. Access the application at http://localhost:8000
    """)

if __name__ == "__main__":
    main() 