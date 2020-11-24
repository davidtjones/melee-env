import configparser
from pathlib import Path
from src.config.config import project_info

class Project:
    def __init__(self, silent=False):
        self.config = project_info
             
        # setup paths
        self.root = Path(self.config['root'])

        self.iso = None
        if 'iso' in self.config:
            self.iso = self.config['iso']

        self.slippi = self.root / "Slippi"
        self.slippi_bin = self.slippi / "squashfs-root/usr/bin"
        self.slippi_config_path = self.root / "Slippi/Slippi_Online-x86_64.AppImage.config/SlippiOnline/Config/Dolphin.ini"

        self.slippi_gecko_ini = self.slippi_bin / "Sys/GameSettings/GALE01r2.ini"

    def use_vulkan(self):
        """Edit config to use Vulkan instead of default OpenGL"""
        
        config = configparser.ConfigParser()
        config.readfp(open(self.slippi_config_path))
        config['Core']['gfxbackend'] = "Vulkan"

        with open(str(self.slippi_config_path), 'w') as outfile:
            config.write(outfile)

    def use_opengl(self):
        config = configparser.ConfigParser()
        config.readfp(open(self.slippi_config_path))
        config['Core']['gfxbackend'] = ""

        with open(str(self.slippi_config_path), 'w') as outfile:
            config.write(outfile)

    def set_ff(self, enable=True):
        """Edit GALE01r2.ini to enable fast forward. Useful for faster training"""
        with open(str(self.slippi_gecko_ini), 'r') as f:
            data = f.readlines()

        if "Fast Forward" not in data[18]:
            exit(f"Error: cannot locate Fast Forward Gecko code in "
                 "{self.slippi_gecko_ini}, please ensure it is located in this "
                 "file, and that it is on line 19!")

        if data[18][0] == "-" and enable: 
            data[18] = "$Optional: Fast Forward\n"
            with open(str(self.slippi_gecko_ini), 'w') as f:
                f.writelines(data)

        elif data[18][0] == "$" and not enable:
            data[18] = "-Optional: Fast Forward\n"
            with open(str(self.slippi_gecko_ini), 'w') as f:
                f.writelines(data)

        else:
            return


