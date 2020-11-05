from torch.utils.data import Dataset, DataLoader
import pandas as pd

class MeleeDataset(Dataset):

    def __init__(self, csv_file, transform=None):
        """
        This may have undergo several iterations. Do we need to be able to load
        a whole game file, or just a series of frames? If the latter, that 
        might get a lot more complex
        """

        self.csv_file = csv_file
        self.df = pd.read_csv(self.csv_file)
        self.transform=transform

    def __len__(self):
        return len(self.df)

    def __getitem__(self, idx):
        
        sample = self.df.iloc[idx]

        if self.transform:
            sample = self.transform(sample)

        return sample


