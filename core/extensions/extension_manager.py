import os
import json
import zipfile
import shutil
from pathlib import Path

class ExtensionManager:
    def __init__(self):
        self.extensions_dir = os.path.join(os.path.expanduser("~"), ".pycursor", "extensions")
        os.makedirs(self.extensions_dir, exist_ok=True)

    def install_vsix(self, vsix_path):
        """
        Installs a .vsix file (which is just a zip file).
        """
        try:
            with zipfile.ZipFile(vsix_path, 'r') as zip_ref:
                # Read package.json to get ID/name
                package_json_data = None
                try:
                    with zip_ref.open('extension/package.json') as f:
                        package_json_data = json.load(f)
                except KeyError:
                    # Some vsix might differ, but standard is extension/package.json
                    return False, "Invalid VSIX structure: package.json not found"

                publisher = package_json_data.get('publisher', 'unknown')
                name = package_json_data.get('name', 'unknown')
                version = package_json_data.get('version', '0.0.0')
                
                extension_id = f"{publisher}.{name}-{version}"
                target_dir = os.path.join(self.extensions_dir, extension_id)
                
                if os.path.exists(target_dir):
                    shutil.rmtree(target_dir)
                
                # Extract
                zip_ref.extractall(target_dir)
                
                # Move contents from 'extension' subdir to root of target_dir if typical structure
                extension_subdir = os.path.join(target_dir, "extension")
                if os.path.exists(extension_subdir):
                    for item in os.listdir(extension_subdir):
                        shutil.move(os.path.join(extension_subdir, item), target_dir)
                    os.rmdir(extension_subdir)
                    
                return True, f"Installed {name} v{version}"
        except Exception as e:
            return False, str(e)

    def get_installed_extensions(self):
        """
        Returns a list of dicts with extension info.
        """
        extensions = []
        if not os.path.exists(self.extensions_dir):
            return extensions
            
        for d in os.listdir(self.extensions_dir):
            path = os.path.join(self.extensions_dir, d)
            if os.path.isdir(path):
                pkg_path = os.path.join(path, "package.json")
                if os.path.exists(pkg_path):
                    try:
                        with open(pkg_path, "r", encoding="utf-8") as f:
                            data = json.load(f)
                            extensions.append({
                                "name": data.get("displayName", data.get("name")),
                                "id": f"{data.get('publisher')}.{data.get('name')}",
                                "version": data.get("version"),
                                "description": data.get("description", ""),
                                "publisher": data.get("publisher"),
                                "path": path
                            })
                    except:
                        pass
        return extensions
