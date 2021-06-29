import os
import time
import json
from pathlib import Path
import argparse
import subprocess
import requests
import shutil
import signal
import configparser
from tqdm import tqdm

def download_file(url):
    local_filename = url.split('/')[-1]
    # NOTE the stream=True parameter below
    with requests.get(url, stream=True) as r:
        total_size_in_bytes= int(r.headers.get('content-length', 0))
        progress_bar = tqdm(
            total=total_size_in_bytes, 
            unit='iB', 
            unit_scale=True,
            desc=f"Downloading {local_filename}")

        r.raise_for_status()
        with open(local_filename, 'wb') as f:
            for chunk in r.iter_content(chunk_size=8192): 
                progress_bar.update(len(chunk))
                f.write(chunk)

    progress_bar.close()
    return Path(local_filename).resolve()

def install_slippi(cwd_str):
    if not (cwd_str / "Slippi/squashfs-root").exists():
        # windows support!?
        appimg_url = r"https://github.com/project-slippi/Ishiiruka/releases/latest/download/Slippi_Online-x86_64.AppImage"
        (cwd_str / "Slippi").mkdir(parents=True, exist_ok=True)

        # Download latest version of slippi
        appimg_path = download_file(appimg_url)

        # Set as executable
        appimg_path.chmod(509)

        # Place inside Slippi
        appimg_path.rename(appimg_path.parents[0] / "Slippi" / appimg_path.name)
        appimg_path = appimg_path.parents[0] / "Slippi" / appimg_path.name

        os.chdir(str(appimg_path.parents[0]))
        cmd_extract = f"{appimg_path} --appimage-extract"

        # Extract 
        process = subprocess.Popen(cmd_extract.split(), stdout=subprocess.PIPE)
        output, error = process.communicate()

        # Delete executable
        appimg_path.unlink()

def create_config(iso, home):
    if iso:
        iso = Path(iso).resolve()
    if home:
        home = Path(home).resolve()

    with open('config.py', 'w') as fp:
        if not iso:
           data = f'config = {{\n    "root": root_dir,\n    "home": "{home}/""}}\n'
        else:  
           data = f'config = {{\n    "root": root_dir,\n    "home": "{home}/",\n    "iso" : "{iso}"}}'

        print("Writing to file:")
        print(data)
        fp.write("from pathlib import Path\n")
        fp.write("root_dir = Path(__file__).parent\n")
        fp.write(data)

def apply_gecko_codes(root):
    # get most up-to-date codes:
    gale01r2_url = "https://raw.githubusercontent.com/altf4/slippi-ssbm-asm/libmelee/Output/Netplay/GALE01r2.ini"
    gale01r2_path = download_file(gale01r2_url)
    gale01r2_path_new = root / "extra/GALE01r2.ini"
    gale01r2_path.rename(gale01r2_path_new)
    gale01r2_path = gale01r2_path_new

    # Locate and rename old ini
    slippi_gecko_ini = root / "Slippi/squashfs-root/usr/bin/Sys/GameSettings/GALE01r2.ini"
    slippi_gecko_ini.rename(str(slippi_gecko_ini.parents[0] / "GALE01r2.ini.old"))

    # Copy the required codes to the old location
    dest = shutil.copy(str(gale01r2_path), str(slippi_gecko_ini))

    # Add the fastforward code at the end of this file:
    fast_forward = open(root / "extra/fast_forward").read()
    with open(str(slippi_gecko_ini), 'a') as f:
        f.write("\n")
        f.write(fast_forward)

    # Add the fast forward code to the [Gecko_Enabled] section
    with open(str(slippi_gecko_ini), 'r') as f:
        data = f.readlines()

    # I think the below can probably be done more cleanly with configparser
    # turn off recommended: apply delay to all in-game scenes
    if data[13] == "$Recommended: Apply Delay to all In-Game Scenes\n":
        data[13] = "-" + data[13][1:]  # turn this off

    # check that line 15 is empty before we start adding stuff
    if data[14] != "\n":
        exit("Something has gone wrong... check that {slippi_gecko_ini} exists and matches the one found in src/extra")

    data.insert(14, "-Optional: Fast Forward\n")
    data.insert(14, "-Optional: Flash Red on Failed L-Cancel\n")
    data.insert(14, "$Optional: Center Align 2P HUD\n")
    data.insert(14, "$Optional: Disable Screen Shake\n")
    data.insert(14, "-Optional: Widescreen 16:9\n")

    with open(str(slippi_gecko_ini), 'w') as f:
        f.writelines(data)

def configure_dolphin(root):
    slippi_config_path = root / "Slippi/data//Config/Dolphin.ini"

    if not slippi_config_path.exists():
        exit(f"Error: no Slippi Config. Run Slippi Online once to generate these files"
             f"Then confirm that files exist in {slippi_config_path}")
    else:
        print("Found dolphin config")

    config = configparser.ConfigParser()
    config.read_file(open(slippi_config_path))
    config['Core']['SlippiReplayDir'] = f"{root / 'Slippi/replays'}"
    config['Core']['SlippiReplayMonthFolders'] = "True"

    with open(str(slippi_config_path), 'w') as outfile:
        config.write(outfile)
     
    # Link this config to the extracted dolphin
    user_path = root / "Slippi/squashfs-root/usr/bin/User"
    user_path.mkdir(parents=True, exist_ok=True)

    config_path = user_path / "Config"
    config_path.symlink_to(root / "Slippi/data/Config")

    # Move GCPadNew.ini to this location
    shutil.copy(
        str(root / "extra/GCPadNew.ini"), 
        str(root / "Slippi/data/Config/GCPadNew.ini"))
