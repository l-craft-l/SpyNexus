from core.display import display_error, write_effect, maRed
from subprocess import run

def launch(cmd):
    try:
        return run(cmd, shell=True, capture_output=False)
    except Exception as err:
        raise Exception(f"{display_error} Fatal error has ocurred... {maRed(err)}")
