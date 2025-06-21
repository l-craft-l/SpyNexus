import os
from core.display import (
    maGreen, maBold, display_validate, pointing, maMagenta, write_effect
)

def save_data(file, title, text, pr, show):
    generated_spy_nexus = 'File generated and created by SpyNexus.\nCreator and Developer: l-craft-l\n'

    if not os.path.exists(file):
        with open(file, pr) as file_data:
            file_data.write(generated_spy_nexus)

    with open(file, pr) as file_data:
        if title:
            file_data.write(title + '\n')
        if text:
            file_data.write(text + '\n')

    if show:
        write_effect(f"\n{display_validate} Saved successfully the info in: '{maBold(file)}' {maMagenta(pointing)}", 0.05)
