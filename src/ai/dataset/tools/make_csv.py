import pandas as pd
import numpy as np
import melee
import code
from pathlib import Path
from tqdm import tqdm
from multiprocessing import Pool
from slippi import Game


if __name__ == "__main__":
    
    def work(path):
        try:
            game = Game(str(path))
            players = []
            for player in game.start.players:
                if player is not None:
                    players.append(player)

            p1 = players[0].character.name
            p2 = players[1].character.name
            stage = game.start.stage.name
            return [path, p1, p2, stage]
        except:
            return [path, "err", "err", "err"]
    
    dataset_path = Path("../slp-dataset/")
    training_path = dataset_path / "training_data"
    training_files = list(training_path.glob("*.slp"))
    print(f"{len(training_files)} files in dataset")

    dataset = pd.DataFrame(columns=["path", "P1", "P2", "stage"])

    pool = Pool(8)
    for idx, output in enumerate(tqdm(pool.imap_unordered(work, training_files), total=len(training_files))):
        dataset[idx] = output

    dataset_no_err = dataset[dataset.P1 != "err"]
    print(f"{len(dataset) - len(dataset_no_err)} bad examples (?)")
    dataset_no_err.to_csv(dataset_path / "dataset.csv")
