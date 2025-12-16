import os
import json
import shutil
from typing import List, Tuple, Dict

def load_config(config_path: str = "config.json") -> Dict[str, List[str]]:
    """Load file extension rules from config.json with validation."""
    try:
        with open(config_path, "r") as f:
            config = json.load(f)
        if not isinstance(config, dict):
            raise ValueError("Config must be a dictionary.")
        return config
    except Exception as e:
        raise Exception(f"Config error: {str(e)}")

def list_files(folder_path: str) -> List[str]:
    """List all files (excluding directories and system files)."""
    if not os.path.exists(folder_path):
        raise FileNotFoundError(f"Folder does not exist: {folder_path}")
    
    files = []
    for item in os.listdir(folder_path):
        full_path = os.path.join(folder_path, item)
        if os.path.isfile(full_path) and not item.startswith(('.', '~')):
            files.append(full_path)
    return files

def get_destination_folder(filename: str, mapping: Dict[str, List[str]]) -> str:
    """Determine the destination folder based on file extension (case-insensitive)."""
    _, ext = os.path.splitext(filename)
    ext = ext.lower()
    
    for folder, extensions in mapping.items():
        if ext in [e.lower() for e in extensions]:
            return folder
    return "Other_File_Types"  # Default for unmapped extensions

def organize_files(
    folder_path: str,
    mapping: Dict[str, List[str]],
    dry_run: bool = True
) -> List[Tuple[str, str]]:
    """
    Organize files into folders with duplicate handling.
    Returns list of (source, destination) file paths.
    """
    files = list_files(folder_path)
    moves = []

    for src in files:
        filename = os.path.basename(src)
        dest_folder = get_destination_folder(filename, mapping)
        dest_dir = os.path.join(folder_path, dest_folder)
        
        os.makedirs(dest_dir, exist_ok=True)
        
        # Handle duplicates (e.g., "file.txt" → "file_1.txt")
        dest_path = os.path.join(dest_dir, filename)
        counter = 1
        while os.path.exists(dest_path):
            name, ext = os.path.splitext(filename)
            dest_path = os.path.join(dest_dir, f"{name}_{counter}{ext}")
            counter += 1

        moves.append((src, dest_path))

        if not dry_run:
            try:
                shutil.move(src, dest_path)
            except Exception as e:
                moves.remove((src, dest_path))  # Remove failed move
                raise Exception(f"Failed to move {filename}: {str(e)}")

    return moves

def undo_organization(moves: List[Tuple[str, str]]) -> None:
    """Revert file moves while preserving original folder structure."""
    for dest, src in reversed(moves):
        if os.path.exists(dest):
            os.makedirs(os.path.dirname(src), exist_ok=True)
            shutil.move(dest, src)