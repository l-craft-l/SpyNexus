import os
from core.display import display_error, write_effect
from core.ma_command import launch

def sw_fl(file, color, speed=0.0005):
    try:
        with open(file, "r") as arch:
            cont = arch.read()
            write_effect(color(cont), speed)
    except FileNotFoundError: raise Exception(f"{display_error} Error, the file doesn't exist!")

def show_icon(dir, color_icon, color_title, speed=0.0005):
    if not os.path.exists(dir): raise Exception(f"{display_error} Fatal error, the directory doesn't exist!")
    launch("clear")

    for name in sorted(os.listdir(dir)):
        file = os.path.join(dir, name)

        if name.startswith("icon"): sw_fl(file, color_icon, speed)
        if name.startswith("title"): sw_fl(file, color_title, speed)
