import os
import json
from pathlib import Path
import argparse

parser = argparse.ArgumentParser(description='My first melee app!')
parser.add_argument('--iso', '-p', type=str,
                    help='Melee 1.02 ISO, this starts the game more quickly',
                    default="")

args = parser.parse_args()

iso = Path(args.iso)
print(iso)
if not iso.exists():
    print("not a valid path")
    iso = ""

cwd = Path(os.getcwd())

if (cwd / "Slippi/squashfs-root").exists():
    config_path = cwd / "config"
    cwd_str = str(cwd.absolute())
    with open(config_path / 'config.json', 'w') as fp:
        if not iso:
           data = {"root": cwd_str}
        else:  
           data = {"root": cwd_str,
                   "iso" : args.iso}
        print(data)
        json.dump(data, fp, sort_keys=True, indent=4)

else:
    exit("Error: Cannot find squashfs-root. Please ensure that genconfig is " \
         "executed from the src directory and that the appimage has been " \
         "extracted. For more info, see README.md")
    
