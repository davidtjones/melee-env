# This script demonstrates how to launch melee via libmelee with a portable
# installation. Useful for testing installation: confirm that settings 
# are default.

import os
import melee
from pathlib import Path
import json

with open('config/config.json', 'r') as fp:
    config = json.load(fp)

project_root = Path(config['root'])

bin_path = project_root / "Slippi/squashfs-root/usr/bin"

if not bin_path.exists():
    exit("Error: Cannot find squashfs-root, please make sure the AppImage " \
         "has been extracted. For more info, see README.md")

config = project_root / "Slippi/Slippi_Online-x86_64.AppImage.config"
data = project_root / "Slippi/Slippi_Online-x86_64.AppImage.home"

if not config.exists() or not data.exists():
    exit("Error: Cannot find portable installation directories, please " \
         "create these via --appimage-portable-{home, config}")

print(f"Setting $XDG_DATA_HOME to {data}")
print(f"Setting $XDG_CONFIG_HOME to {config}")

os.environ["XDG_DATA_HOME"] = str(data)
os.environ["XDG_CONFIG_HOME"] = str(config)

console = melee.Console(path=str(bin_path))
console.run()
console.connect()


