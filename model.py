import torch
from torch import nn, optim
import os


class Q(nn.Module):
    def __init__(self, input, intermediate, output):
        super().__init__()
        self.transition1 = nn.Linear(input, intermediate)
        self.transition2 = nn.Linear(intermediate, output)

    def forward(self, n):
        n = nn.functional.relu(self.transition1(n))
        return self.transition2(n)

class QTrainer:
    def __init__(self, model, discout_rate, learning_rate):
        self.discount_rate = discout_rate
        self.model = model
        self.optim = torch.optim.Adam(model.parameters(), lr=learning_rate)
        self.crit = nn.MSELoss()
    
    def train(self, curr_state, new_state, action, reward, game_over):
        curr_state = torch.tensor(curr_state, dtype=torch.float)
        new_state = torch.tensor(new_state, dtype=torch.float)
        action = torch.tensor(action, dtype=torch.long)
        reward = torch.tensor(reward, dtype=torch.float)

        if len(curr_state.shape) == 1:
            curr_state = torch.unsqueeze(curr_state, 0)
            new_state = torch.unsqueeze(new_state, 0)
            action = torch.unsqueeze(action, 0)
            reward = torch.unsqueeze(reward, 0)
            game_over = (game_over, )
        
        prediction = self.model(curr_state)
        t = prediction.clone()
        
        for i in range(len(game_over)):
            newQ = reward[i]
            if not game_over[i]:
                newQ = reward[i] + self.discount_rate * torch.max(self.model(new_state[i]))
            t[i][torch.argmax(action[i]).item()] = newQ
        
        self.optim.zero_grad()
        loss = self.crit(t, prediction)
        loss.backward()
        self.optim.step()