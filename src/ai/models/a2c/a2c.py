import torch
import torch.nn as nn


# Networks

class Debug(nn.Module):
    def __init__(self):
        super().__init__()

    def forward(self, x):
        print(x)
        print(x.shape)
        return x

class ActorCritic(nn.Module):
    def __init__(self, 
                 input_size, 
                 output_size, 
                 idx_cat,
                 emb_dims,
                 mlp_dims,
                 emb_dropout=0.1,
                 lin_dropout=0.1):

        # input_size: number of input features
        # output_size: action space size for actor
        # idx_cat: list of indices correspoding to categorical features
        # emb_dims: list of tuples (emb_size, emb_dim) of each categorical feature
        #   corresponding to idx_cat
        # emb_dropout: desired dropout on embedding layers
        # lin_dropout: desired dropout on linear layers

        super().__init__()
        self.idx_cat = idx_cat

        self.idx_con = []
        for i in range(input_size):
            if i not in idx_cat:
                self.idx_con.append(i)


        self.embeddings = []
        self.emb_dropout = []
        embed_length = 0
        for idx, categorical_feature in enumerate(idx_cat):
            self.embeddings.append(nn.Embedding(emb_dims[idx][0], emb_dims[idx][1]))
            self.emb_dropout.append(nn.Dropout(emb_dropout))
            embed_length += emb_dims[idx][1]

        con_length = len(self.idx_con)
        # normalize continuous features
        self.continuous_batchnorm = nn.BatchNorm1d(con_length)


        self.MLP = []
        self.MLP.append(nn.Linear(con_length+embed_length, mlp_dims[0]))

        for i in range(len(mlp_dims)-1):
            self.MLP.append(nn.Linear(mlp_dims[i], mlp_dims[i+1]))
            self.MLP.append(nn.LeakyReLU(0.05))

        self.MLP.append(nn.Linear(mlp_dims[-1], output_size))
        self.MLP = nn.Sequential(*self.MLP)


    def forward(self, x):
        b = x.shape[0]
        # feed categorical features through embeddings first
        embedded_cat = []
        categorical = x[:, self.idx_cat].long()
        for idx, categorical_feature in enumerate(self.idx_cat):
            embedded_cat.append(
                # apply the embedding for categorical feature `x_idx` with 
                #   embedding `embedding_idx`
                self.embeddings[idx](categorical[:, idx]))

        embedding = torch.cat(embedded_cat, dim=1)

        x_cont = x[:, self.idx_con]

        feature_vector = torch.cat((embedding, x_cont), dim=1)
        
        return self.MLP(feature_vector)
        

class A2C(nn.Module):
    def __init__(self, actor, critic):
        super().__init__()

        self.actor = actor
        self.critic = critic

    def forward(self, state):
        action = self.actor(state)
        value = self.critic(state)

        return action, value



if __name__=="__main__":
    # test an input:
    input = torch.tensor([
        4, 0, 4, 0, 
        2, 2, 0, 0, 
        1, 0, 246, -246, 100, -100,
        200, 129, 3, 20])

    net_test = ActorCritic(input.shape[0], 45, 
                           [8, 9, 14, 15],
                           [(2, 1), (2, 1), (383, 200), (383, 200)],
                           [128, 128, 128])

    output = net_test(input)
    print(output)
            

