import configparser
from src.config.project import Project


def toggle_mute(p):
    slippi_config_path = p.root/"Slippi/Slippi_Online-x86_64.AppImage.config/SlippiOnline/Config/Dolphin.ini"

    if not slippi_config_path.exists():
        exit(f"Error, no dolphin config. Run Slippi once to generate thes files")

    print("Found dolphin config")

    config = configparser.ConfigParser()
    config.readfp(open(slippi_config_path))
    curr_backend = config['DSP']['backend']
    if curr_backend == "ALSA":
        new_backend = "No audio output"  # reset to default
    else:
        new_backend = "ALSA"

    config['DSP']['backend'] = new_backend
    with open(slippi_config_path, 'w') as outfile:
        config.write(outfile)

    print(f"Volume adjusted to {new_backend}")

if __name__=="__main__":
    p = Project()
    toggle_mute(p)
