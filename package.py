import os
import subprocess
import sys

def package():
    """
    Package PyCursor IDE using PyInstaller.
    """
    print("🚀 Starting PyCursor packaging process...")
    
    # Check if pyinstaller is installed
    try:
        import PyInstaller
    except ImportError:
        print("❌ PyInstaller not found. Installing...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "pyinstaller"])

    # Define paths
    main_script = "main.py"
    app_name = "PyCursor"
    icon_path = os.path.join("assets", "icons", "logo.ico") # Assuming logo.ico exists or uses default
    
    # Resources to include
    add_data = [
        ("assets", "assets"),
        ("config", "config"),
    ]
    
    # Build command
    cmd = [
        "pyinstaller",
        "--noconfirm",
        "--onefile",
        "--windowed",
        f"--name={app_name}",
    ]
    
    if os.path.exists(icon_path):
        cmd.append(f"--icon={icon_path}")
    
    for src, dst in add_data:
        cmd.append(f"--add-data={src}{os.pathsep}{dst}")
    
    cmd.append(main_script)
    
    print(f"📦 Running command: {' '.join(cmd)}")
    
    try:
        subprocess.check_call(cmd)
        print("✅ Packaging completed successfully!")
        print(f"📁 You can find the executable in the 'dist' folder.")
    except subprocess.CalledProcessError as e:
        print(f"❌ Packaging failed with error: {e}")

if __name__ == "__main__":
    package()
