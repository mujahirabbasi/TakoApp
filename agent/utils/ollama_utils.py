import os
import sys
import requests
import subprocess
import time

def get_ollama_path():
    """Get the path to the Ollama executable based on the operating system."""
    if sys.platform == "win32":
        # Check multiple possible installation locations
        possible_paths = [
            os.path.join(os.environ.get('ProgramFiles', 'C:\\Program Files'), 'Ollama', 'ollama.exe'),
            os.path.join(os.environ.get('ProgramFiles(x86)', 'C:\\Program Files (x86)'), 'Ollama', 'ollama.exe'),
            os.path.join(os.environ.get('LOCALAPPDATA', 'C:\\Users\\%USERNAME%\\AppData\\Local'), 'Programs', 'Ollama', 'ollama.exe'),
            os.path.join(os.environ.get('APPDATA', 'C:\\Users\\%USERNAME%\\AppData\\Roaming'), 'Ollama', 'ollama.exe')
        ]
        for path in possible_paths:
            if os.path.exists(path):
                return path
        raise FileNotFoundError("""
Ollama is not installed or not found in the expected locations. Please follow these steps:

1. Download Ollama for Windows:
   - Go to https://ollama.ai/download
   - Click on the Windows download button
   - Run the installer

2. After installation:
   - Start Ollama from your Start menu
   - Wait for it to start completely
   - Then run this script again

If you've already installed Ollama in a custom location, please add it to your system's PATH environment variable.
""")
    return "ollama"  # For non-Windows systems

def check_ollama_availability():
    """Check if Ollama is running and available."""
    try:
        response = requests.get("http://localhost:11434/api/tags")
        return response.status_code == 200
    except requests.exceptions.ConnectionError:
        return False

def wait_for_ollama(timeout=60):
    """Wait for Ollama to become available."""
    start_time = time.time()
    while time.time() - start_time < timeout:
        if check_ollama_availability():
            return True
        time.sleep(5)
    return False

def check_and_pull_model(model_name="llama2"):
    """Check if model exists and pull it if it doesn't."""
    try:
        response = requests.get(f"http://localhost:11434/api/tags")
        models = response.json().get("models", [])
        model_exists = any(model["name"] == model_name for model in models)
        if not model_exists:
            ollama_path = get_ollama_path()
            subprocess.run([ollama_path, "pull", model_name], check=True)
    except Exception as e:
        raise 