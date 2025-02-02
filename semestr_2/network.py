
import numpy as np
import pandas as pd

import torch
from torch import nn
import torch.nn.functional as F

import tqdm


class ThreeInputsNet(nn.Module):
    
    def __init__(self, n_tokens, n_cat_features, concat_number_of_features, hid_size=64):
        
        super(ThreeInputsNet, self).__init__()
        
        #print(hid_size)
        
        self.title_emb = nn.Embedding(n_tokens, embedding_dim=hid_size)
        self.title_conv = nn.Conv1d(in_channels=hid_size, out_channels=hid_size, kernel_size=2)
        self.title_relu = nn.ReLU()
        self.title = nn.AdaptiveAvgPool1d(output_size=1)
        
        self.full_emb = nn.Embedding(n_tokens, embedding_dim=hid_size)
        self.full_conv = nn.Conv1d(in_channels=hid_size, out_channels=hid_size, kernel_size=2)
        self.full_relu = nn.ReLU()
        self.full = nn.AdaptiveAvgPool1d(output_size=1)
        
        #self.category_emb = nn.Embedding(n_cat_features, embedding_dim=hid_size*2)
        self.category = nn.Linear(in_features=n_cat_features, out_features=hid_size)


        # Example for the final layers (after the concatenation)
        self.inter_dense = nn.Linear(in_features=concat_number_of_features, out_features=hid_size*2)
        self.final_dense = nn.Linear(in_features=hid_size*2, out_features=1)

        

    def forward(self, whole_input):
        input1, input2, input3 = whole_input
        
        #print(input1)
        
        title_beg = self.title_emb(input1).permute((0, 2, 1))
        title = self.title(self.title_relu(self.title_conv(title_beg)))
        
        full_beg = self.full_emb(input2).permute((0, 2, 1))
        full = self.full(self.full_relu(self.full_conv(full_beg)))       
        
        category = self.category(input3)
        
        #print(title.size())
        
        #print(full.size())
        
        #print(category.size())
        
        concatenated = torch.cat(
            [
            title.view(title.size(0), -1),
            full.view(full.size(0), -1),
            category.view(category.size(0), -1)
            ],
            dim=1)
        #print(concatenated)
        
        pre_out = self.inter_dense(concatenated)
        out = self.final_dense(pre_out)
        
        return out