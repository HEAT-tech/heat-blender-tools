from flask import Flask, request
import os
from os import environ, path
import platform
import subprocess
import sys
import bpy

app = Flask(__name__)


@app.route('/auth/login', methods=['GET'])
def login():
    auth_token = request.args.get('auth_token')
    bpy.ops.object.loading_indicator_operator()
    print(f'The auth_token is {auth_token}')
    return(f'The auth_token is {auth_token}')


def start():
    from . import dependencies
    print(__file__)

    preinstalled_deps = dependencies.get_preinstalled_deps_path()
    installed_deps = dependencies.get_installed_deps_path()
    log_path = path.join(os.path.dirname(__file__), 'local_server.log')

    env  = environ.copy()
    env['PYTHONPATH'] = installed_deps + os.pathsep + preinstalled_deps
    python_home = path.abspath(path.dirname(sys.executable) + "/..")
    env['PYTHONHOME'] = python_home

    creation_flags = 0
    if platform.system() == "Windows":
        env['PATH'] = env['PATH'] + os.pathsep + path.abspath(path.dirname(sys.executable) + "/../../../blender.crt")
        creation_flags = subprocess.CREATE_NO_WINDOW

    with open(log_path, "wb") as log:
        subprocess.Popen(
            args = [
              sys.executable,
              '-u', __file__,
              '--port', '8960',
              '--server', 'localhost',
            ],
            env = env,
            creationflags = creation_flags,
            stdout = log,
            stderr = log,
        )

def stop():
    pass


if __name__ == '__main__':
    app.run(port=8690)