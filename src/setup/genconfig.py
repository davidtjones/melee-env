import os
import time
from pathlib import Path
import argparse
import subprocess
import signal
from src.setup.setup_helpers import (create_config, install_slippi, 
    apply_gecko_codes, configure_dolphin)

parser = argparse.ArgumentParser(description='ac-bot setup script')
parser.add_argument('--iso', '-p', type=str,
                    help='Melee 1.02 ISO, including this starts the game more quickly',
                    default="")

parser.add_argument('--home-dir', '-d', type=str, help="isolated home directory",
                    default="Slippi/data")

args = parser.parse_args()
if not args.iso:
    iso = None
else:
    iso = Path(args.iso)

home = Path(args.home_dir).resolve()

print("ISO path: ", iso)
print("Isolated Home path: ", home)

if iso and not iso.exists():
    print("not a valid path")
    iso = ""

root = Path(os.getcwd()).resolve()

# This script generates a config.py which contains information about the game 
# ISO and where this directory is located on the user's system. This is used 
# later to load data, change options, etc. 
create_config(iso, home)

# Next, Slippi is downloaded and unpacked. A local data folder is created to 
# keep this installation isolated from another (main) installation of slippi.
install_slippi(Path(root))

# It is necessary to download some gecko codes and install these into dolphin's
# config files. However, Dolphin doesn't generate these files until after being
# run once. We can open and close dolphin, then apply these codes
apprun_path = root / "Slippi/squashfs-root/AppRun"
process = subprocess.Popen(
    str(apprun_path)+f" -u {home.resolve()}", 
    stdout=subprocess.PIPE, 
    shell=True,
    preexec_fn=os.setsid)

time.sleep(2)
os.killpg(os.getpgid(process.pid), signal.SIGTERM) # send kill signal

print("Applying gecko codes...")
apply_gecko_codes(root)

print("Configuring Dolphin")
configure_dolphin(root)

print("Done.")
