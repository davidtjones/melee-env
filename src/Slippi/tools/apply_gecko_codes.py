from src.config.project import Project
import os
import shutil

p = Project()

# Locate and rename old ini
old =  p.slippi_gecko_ini.rename(str(p.slippi_gecko_ini.parents[0] / "GALE01r2.ini.old"))

# Copy the required codes to the old location
new_gecko_ini_path = p.root / "extra/GALE01r2.ini"
dest = shutil.copy(str(new_gecko_ini_path), str(p.slippi_gecko_ini))

# Add the fastforward code at the end of this file:
fast_forward = open("extra/fast_forward").read()
with open(str(p.slippi_gecko_ini), 'a') as f:
    f.write("\n")
    f.write(fast_forward)

# Add the fast forward code to the [Gecko_Enabled] section
with open(str(p.slippi_gecko_ini), 'r') as f:
    data = f.readlines()

# check that line 15 is empty
if data[14] != "\n":
    exit("Something has gone wrong... check that {p.slippi_gecko_ini} exists and matches the one found in src/extra")

data.insert(14, "-Optional: Fast Forward\n")
data.insert(14, "-Optional: Flash Red on Failed L-Cancel\n")
data.insert(14, "$Optional: Center Align 2P HUD\n")
data.insert(14, "$Optional: Disable Screen Shake\n")
data.insert(14, "-Optional: Widescreen 16:9\n")

with open(str(p.slippi_gecko_ini), 'w') as f:
    f.writelines(data)


print("Done.")


