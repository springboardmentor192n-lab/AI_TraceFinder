import torch
import torch.nn as nn
from torchvision import models

class CNN(nn.Module):
    def __init__(self, num_classes):
        super().__init__()
        
        # Load a pre-trained ResNet18 model
        self.net = models.resnet18(weights=models.ResNet18_Weights.DEFAULT)
        
        # Replace the first conv layer to accept 1 channel instead of 3
        original_conv = self.net.conv1
        self.net.conv1 = nn.Conv2d(
            1, original_conv.out_channels, 
            kernel_size=original_conv.kernel_size, 
            stride=original_conv.stride, 
            padding=original_conv.padding, 
            bias=False
        )
        
        # Properly initialize the new 1-channel conv layer using the pre-trained 3-channel weights!
        with torch.no_grad():
            self.net.conv1.weight.copy_(original_conv.weight.sum(dim=1, keepdim=True))
            
        # Modify the final classification layer
        num_ftrs = self.net.fc.in_features
        self.net.fc = nn.Linear(num_ftrs, num_classes)

    def forward(self, x):
        return self.net(x)