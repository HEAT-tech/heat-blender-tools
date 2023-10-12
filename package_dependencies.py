import os
import sys
import platform
import subprocess
import shutil
import venv

def create_venv(venv_dir):
    """Create a virtual environment."""
    venv.create(venv_dir, with_pip=True)

def install_requirements(venv_dir, requirements_file):
    """Install packages from requirements.txt into the virtual environment."""
    pip_exe = os.path.join(venv_dir, 'bin', 'pip') if sys.platform != "win32" else os.path.join(venv_dir, 'Scripts', 'pip.exe')
    subprocess.check_call([pip_exe, 'install', '-r', requirements_file])

def copy_dependencies(venv_dir, dest_dir):
    """Copy installed packages to the destination directory and then zip them."""
    major_version = sys.version_info.major
    minor_version = sys.version_info.minor
    site_packages_dir = os.path.join(venv_dir, 'lib', f'python{major_version}.{minor_version}', 'site-packages')

    # For Windows, the structure is a bit different
    if sys.platform == "win32":
        site_packages_dir = os.path.join(venv_dir, 'Lib', 'site-packages')

    if not os.path.exists(dest_dir):
        os.makedirs(dest_dir)

    for item in os.listdir(site_packages_dir):
        s = os.path.join(site_packages_dir, item)
        d = os.path.join(dest_dir, item)
        if os.path.isdir(s):
            shutil.copytree(s, d, ignore=shutil.ignore_patterns('__pycache__'))
        else:
            shutil.copy2(s, d)

    # Zip the copied dependencies
    shutil.make_archive(os.path.join(dest_dir, "dependencies"), 'zip', dest_dir)
    # Optionally, if you want to remove the copied files after zipping, uncomment the following line:
    # shutil.rmtree(dest_dir)

def main():
    # Determine the OS-specific subdirectory
    os_name = platform.system()
    print(f"installing dependencies for {os_name}")

    # Paths
    current_dir = os.path.dirname(os.path.abspath(__file__))
    requirements_file = os.path.join(current_dir, 'requirements.txt')
    venv_dir = os.path.join(current_dir, 'temp_venv')
    dest_dir = os.path.join(current_dir, 'dependencies', os_name)

    # Create virtual environment, install requirements, and copy dependencies
    create_venv(venv_dir)
    install_requirements(venv_dir, requirements_file)
    copy_dependencies(venv_dir, dest_dir)

    # Cleanup: remove the temporary virtual environment
    shutil.rmtree(venv_dir)

if __name__ == "__main__":
    main()
