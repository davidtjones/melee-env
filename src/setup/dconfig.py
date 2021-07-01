import configparser
from pathlib import Path
from src.config import config
import melee

class DolphinConfig:
    def __init__(self, silent=False):
        self.config = config
             
        # setup paths
        self.root = Path(self.config['root'])
        self.home = Path(self.config['home'])

        self.iso_path = self.config['iso'] if 'iso' in self.config else None          

        self.slippi_path = self.root / "Slippi"
        self.slippi_bin_path = self.slippi_path / "squashfs-root/usr/bin"
        self.config_path = self.root / "Slippi/data/Config/Dolphin.ini"

        self.gecko_codes_path = self.slippi_bin_path / "Sys/GameSettings/GALE01r2.ini"

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
        with open(str(self.gecko_codes_path), 'r') as f:
            data = f.readlines()

        if "Fast Forward" not in data[18]:
            exit(f"Error: cannot locate Fast Forward Gecko code in "
                 "{self.gecko_codes_path}, please ensure it is located in this "
                 "file, and that it is on line 19!")

        if data[18][0] == "-" and enable: 
            data[18] = "$Optional: Fast Forward\n"
            with open(str(self.gecko_codes_path), 'w') as f:
                f.writelines(data)

        elif data[18][0] == "$" and not enable:
            data[18] = "-Optional: Fast Forward\n"
            with open(str(self.gecko_codes_path), 'w') as f:
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
