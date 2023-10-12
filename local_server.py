from aiohttp import web
import aiohttp_cors
import os
from os import environ, path
import platform
import subprocess
import sys
import importlib.util
import socket

def import_from_filepath(filepath):
    # Add the directory containing the module to sys.path
    dir_path = os.path.dirname(os.path.realpath(filepath))
    sys.path.append(dir_path)

    # Load the module
    spec = importlib.util.spec_from_file_location("module_name", filepath)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)

    return module


simple_queue_filepath = path.join(os.path.dirname(__file__), 'simple_queue.py')
simple_queue_module = import_from_filepath(simple_queue_filepath)
SimpleQueue = simple_queue_module.SimpleQueue

app = web.Application()
routes = web.RouteTableDef()
cors = aiohttp_cors.setup(app, defaults={
    "*": aiohttp_cors.ResourceOptions(
        allow_credentials=True,
        expose_headers="*",
        allow_headers="*",
    )
})

def is_port_available(port):
    """Check if a given port is available."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        try:
            s.bind(("0.0.0.0", port))
            return True
        except OSError:
            return False


@routes.get('/auth/login')
async def login(request):
    auth_token = request.rel_url.query.get('auth_token')
    print(f'The auth_token is {auth_token}!!!')
    heat_queue = SimpleQueue('heat_queue.db')
    heat_queue.push('login', {"auth_token": auth_token})
    return web.Response(text=f'The auth_token is {auth_token}')


@routes.post('/download-movement')
async def downloadMovement(request):
    heat_queue = SimpleQueue('heat_queue.db')
    data = await request.json()
    heat_queue.push('downloadMovement', data)
    return web.Response(text=f'Movement ({data["movementID"]}) added to the download queue!')


@routes.get('/ping')
async def ping(request):
    heat_queue = SimpleQueue('heat_queue.db')
    heat_queue.push('pong', {})
    return web.Response(text=f'pong!')


@routes.get('/add-cube')
async def addCube(request):
    heat_queue = SimpleQueue('heat_queue.db')
    heat_queue.push('addCube', {})
    return web.Response(text=f'done.')


@routes.get('/shutdown')
async def shutdown(request):
    print("Shutting down gracefully")
    await request.app.shutdown()
    await request.app.cleanup()
    return web.Response(text="Shutting down")


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
              '-u', __file__
            ],
            env = env,
            creationflags = creation_flags,
            stdout = log,
            stderr = log,
        )


def stop(process):
    process.terminate()


if __name__ == '__main__':
    if is_port_available(8690) == False:
        print("Port 8690 is already in use. Exiting.")
        exit()

    print("Resetting queue database...")
    heat_queue = SimpleQueue('heat_queue.db')
    heat_queue.destroy()

    print("Starting server...")
    app.add_routes(routes)
    for route in list(app.router.routes()):
        cors.add(route)
    web.run_app(app, port=8690)