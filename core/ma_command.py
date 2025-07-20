import requests
from core.display import display_error, write_effect, maRed
from subprocess import run

def launch(cmd):
    try:
        return run(cmd, shell=True, capture_output=False)
    except Exception as err:
        raise Exception(f"{display_error} Fatal error has ocurred... {maRed(err)}")

def check_internet(url="https://google.com"):
    try:
        requests.get(url, timeout=5)
    except Exception:
        write_effect(f"{display_error} No connection detected... Try again later.", 0.05)
        return False

    return True
