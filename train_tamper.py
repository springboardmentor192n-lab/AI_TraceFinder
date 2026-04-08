import os
import torch
import torch.nn as nn
import torch.optim as optim
import cv2
import numpy as np

from torch.utils.data import TensorDataset, DataLoader
from sklearn.model_selection import train_test_split
from model.cnn_model import CNN

print("Starting Tamper Training...")

# -----------------------------
# DATA LOADER (INLINE - FINAL FIX)
# -----------------------------
VALID_EXT = (".jpg", ".jpeg", ".png", ".tif", ".tiff")

def load_tamper_dataset(base_path):
    X, y = [], []

    for label, cls in enumerate(["Original", "Tampered"]):
        main_folder = os.path.join(base_path, cls)

        for root, dirs, files in os.walk(main_folder):
            for file in files:

                if not file.lower().endswith(VALID_EXT):
                    continue

                img_path = os.path.join(root, file)

                if not os.path.isfile(img_path):
                    continue

                img = cv2.imread(img_path, 0)

                if img is None:
                    continue

                img = cv2.resize(img, (128, 128))

                X.append(img / 255.0)
                y.append(label)

    print(f"Loaded {len(X)} images")
    return np.array(X), np.array(y), ["Original", "Tampered"]


# -----------------------------
# LOAD DATA
# -----------------------------
X, y, class_names = load_tamper_dataset("data/Wikipedia_Scans")

print("Dataset shape:", X.shape)

# Safety check
if len(X) == 0:
    print("ERROR: No images loaded. Check dataset path.")
    exit()

# Convert to tensor
X = torch.tensor(X).unsqueeze(1).float()
y = torch.tensor(y)

# -----------------------------
# TRAIN / TEST SPLIT
# -----------------------------
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

train_data = TensorDataset(X_train, y_train)
test_data = TensorDataset(X_test, y_test)

train_loader = DataLoader(train_data, batch_size=16, shuffle=True)
test_loader = DataLoader(test_data, batch_size=16)

# -----------------------------
# MODEL
# -----------------------------
model = CNN(2)

optimizer = optim.Adam(model.parameters(), lr=0.0005, weight_decay=1e-4)
loss_fn = nn.CrossEntropyLoss()

# -----------------------------
# TRAINING
# -----------------------------
epochs = 50

for epoch in range(epochs):
    total_loss = 0

    for batch_X, batch_y in train_loader:

        # Removed noise addition

        outputs = model(batch_X)
        loss = loss_fn(outputs, batch_y)

        optimizer.zero_grad()
        loss.backward()
        optimizer.step()

        total_loss += loss.item()

    print(f"Epoch {epoch+1}/{epochs} Loss: {total_loss:.4f}")

# -----------------------------
# EVALUATION (REAL ACCURACY)
# -----------------------------
model.eval()
with torch.no_grad():
    correct = 0
    total = 0

    for batch_X, batch_y in train_loader:
        outputs = model(batch_X)
        preds = torch.argmax(outputs, 1)

        correct += (preds == batch_y).sum().item()
        total += batch_y.size(0)

accuracy = correct / total if total > 0 else 0

print(f"\nTampering Test Accuracy: {accuracy*100:.2f}%")

# -----------------------------
# SAVE MODEL
# -----------------------------
torch.save({
    'model_state': model.state_dict(),
    'class_names': class_names
}, "tamper_model.pth")

print("Tampering model saved")