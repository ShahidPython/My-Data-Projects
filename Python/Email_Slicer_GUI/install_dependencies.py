#!/usr/bin/env python3
"""Script to install all required dependencies."""
import subprocess
import sys

def install_dependencies():
    """Install all required packages."""
    packages = [
        "questionary>=1.10.0",
        "typer>=0.9.0", 
        "rich>=13.0.0",
        "email-validator>=1.3.0",
        "tldextract>=3.4.0",
    ]
    
    for package in packages:
        print(f"Installing {package}...")
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", package])
        except subprocess.CalledProcessError as e:
            print(f"Failed to install {package}: {e}")
            return False
    
    return True

if __name__ == "__main__":
    print("Installing Email Slicer dependencies...")
    if install_dependencies():
        print("All dependencies installed successfully!")
    else:
        print("Failed to install some dependencies.")
        sys.exit(1)