from src.config.project import Project
import os
import shutil

p = Project()

# Locate and rename old ini
gecko_ini_path = p.slippi / "squashfs-root/usr/bin/Sys/GameSettings/GALE01r2.ini"
old =  gecko_ini_path.rename(str(gecko_ini_path.parents[0] / "GALE01r2.ini.old"))

# Copy the required codes to the old location
new_gecko_ini_path = p.root / "extra/GALE01r2.ini"
dest = shutil.copy(str(new_gecko_ini_path), str(gecko_ini_path))

print("Done.")


