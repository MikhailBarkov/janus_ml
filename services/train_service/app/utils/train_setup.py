import os

import torch

from settings import config


os.environ["DGLBACKEND"] = "pytorch"

device = torch.device(config.ml_device)
