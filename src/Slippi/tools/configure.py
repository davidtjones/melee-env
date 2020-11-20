import os
import json
import configparser
from pathlib import Path
from src.config.project import Project

p = Project()

# Setup the portable dolphin configuration
slippi_config_path = p.root / "Slippi/Slippi_Online-x86_64.AppImage.config/SlippiOnline/Config/Dolphin.ini"

if not slippi_config_path.exists():
    exit("Error: no Slippi Config. Run Slippi Online once to generate these files")
else:
    print("Found dolphin config")

config = configparser.ConfigParser()
config.readfp(open(slippi_config_path))
config['Core']['SlippiReplayDir'] = f"{p.root / 'Slippi/Slippi'}"
config['Core']['SlippiReplayMonthFolders'] = "True"

with open(str(slippi_config_path), 'w') as outfile:
    config.write(outfile)
 
# Link this config to the extracted dolphin
user_path = p.slippi_bin / "User"
user_path.mkdir(parents=True, exist_ok=True)

config_path = user_path / "Config"
config_path.symlink_to(p.slippi / "Slippi_Online-x86_64.AppImage.config/SlippiOnline/Config")

print("Done")






