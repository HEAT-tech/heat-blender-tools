import socket
from . import local_server

def is_port_available(port):
    """Check if a given port is available."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        try:
            s.bind(("0.0.0.0", port))
            return True
        except OSError:
            return False


def start_server_if_not_started():
    if is_port_available(8690) == False:
        print("Port 8690 is already in use. Local server is running.")
        return None

    local_server.start()