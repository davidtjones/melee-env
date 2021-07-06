import configparser
from pathlib import Path
import sys
import melee
import requests
from tqdm import tqdm
import os
import subprocess
import shutil
import time
import signal
from zipfile import ZipFile
import code



class DolphinConfig:
    def __init__(self):

        # setup paths
        self.home = Path.home()
        self.platform = sys.platform
        
        self.module_path = Path(__file__).resolve().parents[0]  # module installation path
        self.install_data_path = self.module_path / "install_data"

        if self.platform == "win32":
            self.data_path = self.home / "AppData/Roaming"
        elif self.platform == "linux":
            self.data_path = self.home / ".local/share"
        elif self.platform == "darwin":
            self.data_path = self.home / "Library/Application Support"

        self.slippi_path = self.data_path / "melee-env" / "Slippi"

        self.slippi_replays_path = self.slippi_path / "replays"

        if self.platform == "linux":
            self.slippi_bin_path = self.slippi_path / "squashfs-root/usr/bin"
            self.squash_fs = self.slippi_path / "squashfs-root"
            self.slippi_home = self.slippi_path / "data"
            self.config_path = self.slippi_home / "Config/Dolphin.ini"
        
        elif self.platform == "win32":
            self.slippi_bin_path = self.slippi_path / "FM-Slippi"
            self.slippi_home = self.slippi_bin_path
            self.config_path = self.slippi_home / "User/Config/Dolphin.ini"
        
        self.slippi_gecko_ini_path = self.slippi_bin_path / "Sys/GameSettings/GALE01r2.ini"
        self.install_data_path = self.module_path / "install_data"

        # check that our local slippi is installed
        if not self.slippi_bin_path.exists():
            # assume this is a new installation?

            # need to download slippi (based on platform!)
            self.install_slippi(self.slippi_path)

            # download gecko codes for slippi
            self.apply_gecko_codes(self.slippi_path)

            # extra configuration steps
            self.configure_dolphin(self.slippi_path)

            print(f"Successfully downloaded, installed, and configured dolphin "
                f" in {self.slippi_path.parents[0]}")

        else:
            # check for updates? might be nice to preserve the current install
            # in case things break. 
            print(f"Found melee-env installation in {self.slippi_path.parents[0]}")


    def use_render_interface(self, interface="opengl"):
        """Edit config to use Vulkan instead of default OpenGL"""
        if interface not in ["vulkan", "opengl"]:
            raise ValueError("unsupported render interface, please select "
                "either 'vulkan' or 'opengl'")

        if interface == "vulkan":
            config = configparser.ConfigParser()
            config.readfp(open(self.config_path))
            config['Core']['gfxbackend'] = "Vulkan"
        else:
            config = configparser.ConfigParser()
            config.readfp(open(self.config_path))
            config['Core']['gfxbackend'] = ""

            with open(str(self.config_path), 'w') as outfile:
                config.write(outfile)

        return

    def set_ff(self, enable=True):
        """Edit GALE01r2.ini to enable fast forward. Useful for faster training"""
        with open(str(self.slippi_gecko_ini_path), 'r') as f:
            data = f.readlines()

        if "Fast Forward" not in data[18]:
            raise FileNotFoundError(f"Error: cannot locate Fast Forward Gecko code in "
                 "{self.slippi_gecko_ini_path}, please ensure it is located in this "
                 "file, and that it is on line 19!")

        if data[18][0] == "-" and enable: 
            data[18] = "$Optional: Fast Forward\n"
            with open(str(self.slippi_gecko_ini_path), 'w') as f:
                f.writelines(data)

        elif data[18][0] == "$" and not enable:
            data[18] = "-Optional: Fast Forward\n"
            with open(str(self.slippi_gecko_ini_path), 'w') as f:
                f.writelines(data)

        return

    def set_center_p2_hud(self, enable=True):
        """Edit GALE01r2.ini to enable/disable centered P2"""
        with open(str(self.slippi_gecko_ini_path), 'r') as f:
            data = f.readlines()

        if "Center Align 2P HUD" not in data[16]:
            raise FileNotFoundError(f"Error: cannot locate Fast Forward Gecko code in "
                 "{self.slippi_gecko_ini_path}, please ensure it is located in this "
                 "file, and that it is on line 19!")

        if data[16][0] == "-" and enable: 
            data[16] = "$" + data[16][1:]
            with open(str(self.slippi_gecko_ini_path), 'w') as f:
                f.writelines(data)

        elif data[16][0] == "$" and not enable:
            data[16] = "-" + data[16][1:]
            with open(str(self.slippi_gecko_ini_path), 'w') as f:
                f.writelines(data)

        return

    def set_controller_type(self, port, controller_type):
        if  not (1 <= int(port) <= 4):
            raise ValueError(f"Port must be 1, 2, 3, or 4. Received value {port}")

        port = int(port)

        if controller_type not in [e for e in melee.enums.ControllerType]:
            raise ValueError(f"Controller type must be one of {{{[e.name+':'+e.value for e in melee.enums.ControllerType]}}}")

        config = configparser.ConfigParser()
        config.readfp(open(self.config_path))
        config['Core'][f'sidevice{str(port-1)}'] = f"{controller_type.value}"

        with open(str(self.config_path), 'w') as outfile:
            config.write(outfile)

        return

    # Initial Configuration and Installation methods below #

    def _download_file(self, url):
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

    def install_slippi(self, install_path):
        if self.platform == "linux":
            target_url = "https://github.com/project-slippi/Ishiiruka/releases/latest/download/Slippi_Online-x86_64.AppImage"

        elif self.platform == "win32":
            target_url = "https://github.com/project-slippi/Ishiiruka/releases/download/v2.3.1/FM-Slippi-2.3.1-Win.zip"
            # raise NotImplementedError("Windows currently not supported at this time.")

        elif self.platform == "darwin":
            target_url = "https://github.com/project-slippi/Ishiiruka/releases/download/v2.3.1/FM-Slippi-2.3.1-Mac.dmg"
            raise NotImplementedError("OSX currently not supported at this time.")

        install_path.mkdir(parents=True, exist_ok=True)

        # Download latest version of slippi
        slippi_game_path = self._download_file(target_url)

        # move to our directory
        slippi_game_path = slippi_game_path.rename(install_path / slippi_game_path.name)

        if self.platform == "linux":
            print("Dolphin will open and then close to generate files")
            # Set as executable
            slippi_game_path.chmod(509)

            os.chdir(str(slippi_game_path.parents[0]))
            cmd_extract = f"{slippi_game_path} --appimage-extract"

            # Extract 
            process = subprocess.Popen(cmd_extract.split(), stdout=subprocess.PIPE)
            output, error = process.communicate()

            apprun_path = self.squash_fs / "AppRun"
            print(f"Running: {str(apprun_path)+f' -u {str(self.slippi_home)}'}")
            process = subprocess.Popen(
                str(apprun_path)+f" -u {str(self.slippi_home)}", 
                stdout=subprocess.PIPE, 
                shell=True,
                preexec_fn=os.setsid)

            time.sleep(2)
            os.killpg(os.getpgid(process.pid), signal.SIGTERM) # send kill signal



        if self.platform == "win32":
            # Extract
            with ZipFile(slippi_game_path, 'r') as zipObj:
                zipObj.extractall(slippi_game_path.parents[0] / "FM-Slippi")

            print(f"Running: {str(self.slippi_bin_path / 'Slippi Dolphin.exe')}")
            process = subprocess.Popen(str(self.slippi_bin_path / "Slippi Dolphin.exe"), stdout=subprocess.PIPE)
            
            time.sleep(2)
            print("Please make a decision to allow slippi-dolphin access to private/public networks...")
            os.kill(process.pid, signal.SIGTERM)

        # Cleanup - Delete executable
        slippi_game_path.unlink()

        

    def apply_gecko_codes(self, install_path):
        # get most up-to-date codes:
        gale01r2_url = "https://raw.githubusercontent.com/altf4/slippi-ssbm-asm/libmelee/Output/Netplay/GALE01r2.ini"
        gale01r2_path = self._download_file(gale01r2_url)

        # Rename the old ini file
        self.slippi_gecko_ini_path.rename(self.slippi_gecko_ini_path.parents[0] / "GALE01r2.ini.old")

        # Copy the required codes to the old location
        dest = shutil.copy(str(gale01r2_path), str(self.slippi_gecko_ini_path))

        # Add the fastforward code at the end of this file:
        fast_forward = open(self.install_data_path / "fast_forward").read()
        with open(str(self.slippi_gecko_ini_path), 'a') as f:
            f.write("\n")
            f.write(fast_forward)

        # Add the fast forward code to the [Gecko_Enabled] section
        with open(str(self.slippi_gecko_ini_path), 'r') as f:
            data = f.readlines()

        # Surely the below can be done more cleanly with configparser
        # turn off recommended: apply delay to all in-game scenes
        if data[13] == "$Recommended: Apply Delay to all In-Game Scenes\n":
            data[13] = "-" + data[13][1:]  # turn this off

        # check that line 15 is empty before we start adding stuff
        if data[14] != "\n":
            raise FileNotFoundError("Something has gone wrong... check that {self.slippi_gecko_ini_path} exists.")

        data.insert(14, "-Optional: Fast Forward\n")
        data.insert(14, "-Optional: Flash Red on Failed L-Cancel\n")
        data.insert(14, "$Optional: Center Align 2P HUD\n")
        data.insert(14, "$Optional: Disable Screen Shake\n")
        data.insert(14, "-Optional: Widescreen 16:9\n")

        with open(str(self.slippi_gecko_ini_path), 'w') as f:
            f.writelines(data)

        # cleanup
        gale01r2_path.unlink()

    def configure_dolphin(self, install_path):
        if not self.config_path.exists():
            raise FileNotFoundError(f"No Slippi Config. Run Slippi Online once to generate these files"
                 f"Then confirm that files exist in {self.config_path}")      

        config = configparser.ConfigParser()
        config.read_file(open(self.config_path))
        config['Core']['SlippiReplayDir'] = str(self.slippi_replays_path)
        config['Core']['SlippiReplayMonthFolders'] = "True"

        with open(str(self.config_path), 'w') as outfile:
            config.write(outfile)
         
        # Link this config to the extracted dolphin
        user_path = self.slippi_bin_path / "User"
        user_path.mkdir(parents=True, exist_ok=True)

        config_path = user_path / "Config"

        if self.platform == "linux":
            config_path.symlink_to(self.config_path.parents[0])

        # Move GCPadNew.ini to this location
        shutil.copy(
            str(self.install_data_path / "GCPadNew.ini"), 
            str(self.config_path.parents[0] / "GCPadNew.ini")
            )

if __name__=="__main__":
    # test installation
    d = DolphinConfig()