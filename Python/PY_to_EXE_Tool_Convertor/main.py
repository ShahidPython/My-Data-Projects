import os
import re
import subprocess
from pathlib import Path
from tkinter import Tk, filedialog, messagebox 
from PIL import Image
from typing import List, Optional, Set

class PyToExeConverter:
    def __init__(self):
        self.root = Tk()
        self.root.withdraw()
        self.setup_ui()

    def setup_ui(self):
        # Could implement a full GUI here with progress bars, etc.
        pass

    def extract_used_folders(self, script_path: Path) -> List[str]:
        folders_found: Set[str] = set()
        try:
            content = script_path.read_text(encoding='utf-8')
            pattern = r'["\']([a-zA-Z0-9_\-/\\]+?)[/\\][a-zA-Z0-9_\-]+\.\w+["\']'
            for match in re.findall(pattern, content):
                clean_path = match.replace("\\", "/").split("/")
                if clean_path:
                    folders_found.add(clean_path[0])
        except Exception as e:
            messagebox.showerror("Read Error", f"Error reading script: {e}")
        return sorted(folders_found)

    def convert_image_to_icon(self, image_path: Path) -> Optional[Path]:
        output_path = image_path.with_suffix('.ico')
        try:
            with Image.open(image_path) as img:
                img.save(output_path, format='ICO', sizes=[(256, 256)])
            return output_path
        except Exception as error:
            messagebox.showerror("Conversion Error", 
                                f"Failed to convert image to .ico: {error}")
            return None

    def build_executable(self, py_path: Path, 
                        resource_folders: Optional[List[str]] = None, 
                        exe_icon: Optional[Path] = None) -> bool:
        if not py_path.exists():
            messagebox.showerror("Error", "Python file not found.")
            return False

        working_dir = py_path.parent
        os.chdir(working_dir)

        command = [
            "pyinstaller",
            "--onefile",
            "--noconfirm",
            "--clean",
            "--log-level=WARN"
        ]

        if exe_icon:
            if exe_icon.suffix.lower() != '.ico':
                converted = self.convert_image_to_icon(exe_icon)
                if converted:
                    command.append(f'--icon="{converted}"')
            else:
                command.append(f'--icon="{exe_icon}"')

        all_folders = set(self.extract_used_folders(py_path))
        if resource_folders:
            all_folders.update(resource_folders)

        for folder in all_folders:
            folder_path = Path(folder).resolve()
            if folder_path.is_dir():
                data_arg = f'"{folder_path}{os.pathsep}{folder}"'
                command.append(f'--add-data={data_arg}')

        command.append(f'"{py_path}"')

        try:
            result = subprocess.run(" ".join(command), shell=True, check=True)
            messagebox.showinfo("Success", "✅ EXE created in the 'dist' folder!")
            return True
        except subprocess.CalledProcessError as e:
            messagebox.showerror("Build Failed", f"Failed to build executable:\n{e}")
            return False

    def select_python_file(self) -> Optional[Path]:
        path = filedialog.askopenfilename(
            title="Select Python File",
            filetypes=[("Python Files", "*.py"), ("All Files", "*.*")]
        )
        return Path(path) if path else None

    def select_icon_file(self) -> Optional[Path]:
        path = filedialog.askopenfilename(
            title="Select Icon Image",
            filetypes=[("ICO Files", "*.ico"), 
                       ("Image Files", "*.png *.jpg *.jpeg"),
                       ("All Files", "*.*")]
        )
        return Path(path) if path else None

    def select_folders(self) -> List[str]:
        folders = []
        while True:
            folder = filedialog.askdirectory(title="Select Folder to Include")
            if not folder:
                break
            folders.append(folder)
            if not messagebox.askyesno("Add More?", "Add another folder?"):
                break
        return folders

    def run(self):
        messagebox.showinfo("Python to EXE", "📁 Select your Python script")
        script_path = self.select_python_file()
        if not script_path:
            messagebox.showerror("Cancelled", "No Python file selected.")
            return

        use_icon = messagebox.askyesno("Icon", "Add an icon?")
        icon_path = self.select_icon_file() if use_icon else None

        add_folders = messagebox.askyesno("Folders", "Add extra folders?")
        extra_folders = self.select_folders() if add_folders else []

        self.build_executable(script_path, extra_folders, icon_path)

if __name__ == "__main__":
    converter = PyToExeConverter()
    converter.run()