# This script demonstrates how to launch melee via libmelee with a portable
# installation. Useful for testing installation: confirm that settings 
# are default.

import os
import sys
import melee
from pathlib import Path
import json
from src.setup.project import Project


p = Project()

if not p.slippi_bin.exists():
    exit("Error: Cannot find squashfs-root, please make sure the AppImage " \
         "has been extracted. For more info, see README.md")
print(p.slippi_bin)
print(p.home)
console = melee.Console(
    path=str(p.slippi_bin),
    dolphin_home_path=str(p.home)+"/",
    tmp_home_directory=False)

console.run(iso_path=p.iso)

print("Connecting to console...")
if not console.connect():
    print("ERROR: Failed to connect to the console.")
    sys.exit(-1)
print("Console connected")


