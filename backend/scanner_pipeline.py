import torch
import torch.nn as nn
import numpy as np
import cv2
import os

# --- 1. Model Architecture ---
class DeepScannerCNN(nn.Module):
    def __init__(self, num_classes):
        super(DeepScannerCNN, self).__init__()
        self.conv1 = nn.Conv2d(1, 32, 3, padding=1)
        self.bn1 = nn.BatchNorm2d(32)
        self.conv2 = nn.Conv2d(32, 64, 3, padding=1)
        self.bn2 = nn.BatchNorm2d(64)
        self.conv3 = nn.Conv2d(64, 128, 3, padding=1)
        self.bn3 = nn.BatchNorm2d(128)
        self.pool = nn.MaxPool2d(2, 2)
        self.dropout = nn.Dropout(0.5)
        self.fc1 = nn.Linear(128 * 4 * 4, 256)
        self.fc2 = nn.Linear(256, num_classes)

    def forward(self, x):
        x = self.pool(torch.relu(self.bn1(self.conv1(x))))
        x = self.pool(torch.relu(self.bn2(self.conv2(x))))
        x = self.pool(torch.relu(self.bn3(self.conv3(x))))
        x = x.view(-1, 128 * 4 * 4)
        x = self.dropout(torch.relu(self.fc1(x)))
        x = self.fc2(x)
        return x

# --- 2. Pipeline Class ---
class ScannerPipeline:
    def __init__(self, model_path, label_map_path, device='cpu'):
        self.device = torch.device(device)
        self.model = None
        self.idx_to_label = {}

        print("Initializing Pipeline...")
        try:
            # Load Label Map
            if not os.path.exists(label_map_path):
                raise FileNotFoundError(f"Label map not found at {label_map_path}")

            label_map = np.load(label_map_path, allow_pickle=True).item()
            self.idx_to_label = {v: k for k, v in label_map.items()}
            num_classes = len(label_map)

            # Load Model
            self.model = DeepScannerCNN(num_classes=num_classes).to(self.device)
            if not os.path.exists(model_path):
                raise FileNotFoundError(f"Model weights not found at {model_path}")

            self.model.load_state_dict(torch.load(model_path, map_location=self.device))
            self.model.eval()
            print(f"Model loaded successfully. Classes: {num_classes}")
        except Exception as e:
            print(f"CRITICAL ERROR loading pipeline: {e}")

    def extract_residual(self, image_path, img_size=32):
        img = None

        # Handle PDF
        if image_path.lower().endswith('.pdf'):
            try:
                from pdf2image import convert_from_path
                pages = convert_from_path(image_path, first_page=1, last_page=1)
                pil_img = pages[0]
                img = np.array(pil_img)
                img = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)
            except Exception as e:
                raise ValueError(f"PDF Error: {e}. Ensure Poppler is installed.")
        else:
            img = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)

        if img is None:
            raise ValueError("Invalid image file")

        # Process Residual
        denoised = cv2.GaussianBlur(img, (5, 5), 0)
        residual = img.astype(np.float32) - denoised.astype(np.float32)
        residual_resized = cv2.resize(residual, (img_size, img_size), interpolation=cv2.INTER_AREA)

        mean, std = np.mean(residual_resized), np.std(residual_resized)
        if std == 0: std = 1
        residual_norm = (residual_resized - mean) / std

        tensor = torch.tensor(residual_norm, dtype=torch.float32).unsqueeze(0).unsqueeze(0)
        return tensor.to(self.device)