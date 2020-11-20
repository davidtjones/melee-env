import code
import torch
import torch.nn as nn
from pathlib import Path
from tqdm import tqdm, trange

from torch.optim import Adam
from torch.optim.lr_scheduler import CyclicLR
from torch.utils.data import DataLoader

from src.dataset.tools.melee_dataset import MeleeDataset
from src.training.forward_pass import forward_pass
from src.model.simple import SimpleModel

b_size=1
num_workers=6
episodes=2
test_episodes=10
gpu = torch.device('cuda:0')

results_path = Path(f"results/{SimpleModel.__class__.__name__}")
results_path.mkdir(parents=True, exist_ok=True)

print(f"Starting training with b_size {b_size}")

phases = ['train', 'test']
csvs = {"train": "dataset/slp-dataset/training.csv"}
datasets = {k: MeleeDataset(v) for k,v in csvs.items()} 
dataloaders = {k: DataLoader(csvs[k]) for k,v in csvs.items()}

model = SimpleModel(input_size=30)  # not sure about this yet
model.to(device=gpu)
criterion = nn.BCEWithLogitsLoss()
optimizer = Adam(model.parameters())

best_reward = 0
pbar1 = tqdm(range(episodes), total=episode, desc=f"Best Reward: {best_reward}")
for episode in pbar1:
    for phase in phases:
        if phase is 'train':
            model.train()
            pbar2 = tqdm(
                dataloaders['train'], 
                total=len(dataloaders['train']), 
                leave=False,
                desc=f"   Train: {episode+1}/{episode}")

            for idx, batch in enumerate(pbar2):
                output = forward_pass(
                    model, 
                    phase,
                    batch,
                    criterion,
                    optimizer,
                    gpu)
                
                running_loss += output['loss'].item() * b_size
                total += b_size
            running_loss /= len(dataloaders[phase])

        else:
            model.eval()
            for _ in range(test_episodes):
                # idea 1: run dolphin, measure cumulative reward over 
                # `test_episodes` games. If cumulative reward > best_reward,
                # save new model. Some way to supplement learning here? Need
                # to be able to start games automatically for this!!!

                # idea 2: create test dataset split and measure loss
                print("not implemented")

    total = 0.0

    for idx, batch in enumerate(pbar2):
        output = forward_pass(model, 'train', batch, criterion, optimizer, gpu)
        # running_loss += output['loss'].item() * b_size
        # pbar2.set_postfix({
        #    "loss" : f"{running_loss/(idx+1):.3f}",
        #    "lr": f"{optimizer.param_groups[0]['lr']:.2E}"})

        total += b_size
    
    running_loss /= len(dataloaders[phase])

    if phase == 'test':
        if running_loss < best_loss:
            new_ckpt_path = results_path / f"episoze={episode}.pt"
            torch.save(model.state_dict(), new_ckpt_path)
                
            if ckpt_path:
                ckpt_path.unlink() # delete previous checkpoint
            ckpt_path = new_ckpt_path

            best_loss = running_loss
            pbar1.set_description(f"Best Reward: {best_reward:.3f}")
            pbar1.set_postfix({"ckpt": f"{episode}"})

