import json
import os
from pathlib import Path

class Project:
    def __init__(self, silent=False):
        with open('config/config.json', 'r') as fp:
            self.config = json.load(fp)
            
        
        # setup paths
        self.root = Path(self.config['root'])
        if 'iso' in self.config:
            self.iso = self.config['iso']
        else:
            self.iso = None
        self.slippi = self.root / "Slippi"
        self.slippi_bin = self.slippi / "squashfs-root/usr/bin"

