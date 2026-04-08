import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import TensorDataset, DataLoader
from dataset_loader import load_dataset
from model.cnn_model import CNN

# Load Data
X, y, class_names = load_dataset("data/Flatfield")

X = torch.tensor(X).unsqueeze(1).float()
y = torch.tensor(y)

# Create DataLoader (IMPORTANT)
dataset = TensorDataset(X, y)
loader = DataLoader(dataset, batch_size=64, shuffle=True)

# Model
model = CNN(len(class_names))
optimizer = optim.Adam(model.parameters(), lr=0.0005, weight_decay=1e-4)
loss_fn = nn.CrossEntropyLoss()

# Training
epochs = 50

for epoch in range(epochs):
    total_loss = 0

    for batch_X, batch_y in loader:
        outputs = model(batch_X)
        loss = loss_fn(outputs, batch_y)

        optimizer.zero_grad()
        loss.backward()
        optimizer.step()

        total_loss += loss.item()

    print(f"Epoch {epoch+1}/{epochs} Loss: {total_loss:.4f}")

# Accuracy
model.eval()
with torch.no_grad():
    preds = torch.argmax(model(X), 1)
    accuracy = (preds == y).float().mean()

print(f"\nTraining Accuracy: {accuracy.item()*100:.2f}%")

# Save
torch.save({
    'model_state': model.state_dict(),
    'class_names': class_names
}, "model.pth")

print("Model saved successfully")