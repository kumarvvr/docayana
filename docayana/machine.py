import socket


def machine_name() -> str:
    """Name of the host this process runs on, so logs show which dev machine started it."""
    return socket.gethostname()
