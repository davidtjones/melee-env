# This script demonstrates how to launch melee via libmelee with a portable
# installation. Useful for testing installation: confirm that settings 
# are default.

import os
import melee
from pathlib import Path
import json
from src.config.project import Project


p = Project()

if not p.slippi_bin.exists():
    exit("Error: Cannot find squashfs-root, please make sure the AppImage " \
         "has been extracted. For more info, see README.md")

console = melee.Console(path=str(p.slippi_bin))
console.run()
console.connect()


