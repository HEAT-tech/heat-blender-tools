import logging
import os
import platform
import shutil
import subprocess
import sys
import time
from os import environ, makedirs, path, pathsep

from typing import Tuple

from . import global_vars

bk_logger = logging.getLogger(__name__)


def ensure_preinstalled_deps_copied():
    """Copy or unzip dependencies for current platform and python version if applicable.
    Bundled dependencies might be already copied.
    Or their python version might be different from python in currently running Blender.
    """
    if not bundled_version_is_correct():
        bundled = global_vars.BUNDLED_FOR_PYTHON
        bk_logger.warning(f'Skipping dependencies copy: bundled for python {bundled}, running on python {sys.version}')
        return

    deps_path = path.join(path.dirname(__file__), f"dependencies/{platform.system()}")
    deps_path = path.abspath(deps_path)
    install_into = get_preinstalled_deps_path()

    zip_file_path = path.join(deps_path, "dependencies.zip")

    if not path.isdir(install_into):
        if path.isfile(zip_file_path):
            # If dependencies.zip is present, unzip its contents
            bk_logger.warning(f'Unzipping dependencies from {zip_file_path} into {install_into}')
            shutil.unpack_archive(zip_file_path, install_into)
            return
        # If dependencies.zip is not present and the target directory doesn't exist, copy the dependencies
        bk_logger.warning(f'Copying dependencies from {deps_path} into {install_into}')
        shutil.copytree(deps_path, install_into)


def bundled_version_is_correct() -> bool:
    """Check if bundled dependencies are for the major python version of currently running Blender."""
    bundled_major_version = int(global_vars.BUNDLED_FOR_PYTHON.split('.')[0])
    return bundled_major_version == sys.version_info.major

def get_deps_directory_path() -> str:
  """Get path where dependencies (preinstalled and installed) should/are installed for this version of addon."""
  this_dir = os.path.dirname(os.path.realpath(__file__))
  addon_version = f'heat-tools-{global_vars.VERSION}'
  blender_python_version = f'{sys.version_info.major}-{sys.version_info.minor}'
  install_path = path.join(this_dir, 'dependencies', addon_version, blender_python_version)
  return path.abspath(install_path)


def get_installed_deps_path() -> str:
  """Get path to installed dependencies directory. Here addon will install external modules if needed."""
  installed_path = path.join(get_deps_directory_path(), 'installed')
  return path.abspath(installed_path)


def get_preinstalled_deps_path() -> str:
  """Get path to preinstalled modules for current platform."""
  preinstalled_path = path.join(get_deps_directory_path(), 'preinstalled')
  return path.abspath(preinstalled_path)


def add_installed_deps_path():
  """Add installed dependencies directory path into PATH."""
  installed_path = get_installed_deps_path()
  makedirs(installed_path, exist_ok=True)
  sys.path.insert(0, installed_path)

def add_preinstalled_deps_path():
  """Add preinstalled dependencies directory path into PATH."""
  sys.path.insert(0, get_preinstalled_deps_path())


def ensure_deps():
  """Make sure that dependencies which need installation are available. Install dependencies if needed."""
  tried = 0
  while tried < 2:
    tried = tried + 1
    try:
      import aiohttp
      import certifi
      from aiohttp import web, web_request
      import aiohttp_cors
      return
    except:
      bk_logger.warning('dependency missing, installing via pip.')
      install_dependencies()

def install_dependencies():
  """Install pip and install dependencies."""
  started = time.time()
  env  = environ.copy()
  if platform.system() == "Windows":
    env['PATH'] = env['PATH'] + pathsep + path.abspath(path.dirname(sys.executable) + "/../../../blender.crt")

  command = [sys.executable, '-m', 'ensurepip', '--user']
  result = subprocess.run(command, env=env, capture_output=True, text=True)
  bk_logger.warning(f"PIP INSTALLATION:\ncommand {command} exited: {result.returncode},\nstdout: {result.stdout},\nstderr: {result.stderr}")

  requirements = path.join(path.dirname(__file__), 'requirements.txt')
  command = [sys.executable, '-m', 'pip', 'install', '--upgrade', '-t', get_installed_deps_path(), '-r', requirements]
  result = subprocess.run(command, env=env, capture_output=True, text=True)
  bk_logger.warning(f"AIOHTTP INSTALLATION:\ncommand {command} exited: {result.returncode},\nstdout: {result.stdout},\nstderr: {result.stderr}")
  if result.returncode == 0:
    bk_logger.warning(f"Install succesfully finished in {time.time()-started}")
    return

  bk_logger.warning("Install from requirements.txt failed, trying with unconstrained versions...")
  command = [sys.executable, '-m', 'pip', 'install', '--upgrade', '-t', get_installed_deps_path(), 'aiohttp', 'certifi']
  result = subprocess.run(command, env=env, capture_output=True, text=True)
  bk_logger.warning(f"UNCONSTRAINED INSTALLATION:\ncommand {command} exited: {result.returncode},\nstdout: {result.stdout},\nstderr: {result.stderr}")
  if result.returncode == 0:
    bk_logger.warning(f"Install succesfully finished in {time.time()-started}")
    return
  
  bk_logger.critical("Installation failed")
