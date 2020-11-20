import os
import json
from pathlib import Path
import subprocess

with open('config/config.json', 'r') as fp:
    config = json.load(fp)

project_root = Path(config['root'])

if (project_root / "Slippi/Slippi_Online-x86_64.AppImage").exists():
    print("Found Slippi AppImage!")

else:
    exit("Error: Could not locate Slippi Online AppImage! Ensure that " \
         "Slippi_Online-x86_64.AppImage is located in the Slippi folder!")

# appimage-extact puts output in cwd
os.chdir(project_root / "Slippi")

slippi_app_image = project_root / "Slippi/Slippi_Online-x86_64.AppImage"
cmd_extract = f"{slippi_app_image} --appimage-extract"
cmd_config  = f"{slippi_app_image} --appimage-portable-config"
cmd_data    = f"{slippi_app_image} --appimage-portable-home"

# Extract 
process = subprocess.Popen(cmd_extract.split(), stdout=subprocess.PIPE)
output, error = process.communicate()

# Make portable
process = subprocess.Popen(cmd_config.split(), stdout=subprocess.PIPE)
output, error = process.communicate()

process = subprocess.Popen(cmd_data.split(), stdout=subprocess.PIPE)
output, error = process.communicate()
