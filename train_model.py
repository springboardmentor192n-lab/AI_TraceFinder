import cv2
import os
import numpy as np
import pickle
from sklearn.svm import SVC
from sklearn.preprocessing import StandardScaler

datasets = [
    "Dataset/Flatfield",
    "Dataset/Official",
    "Dataset/Wikipedia"
]

X=[]
y=[]

print("Extracting Features...")

for base in datasets:

    for scanner in os.listdir(base):

        scanner_path = base + "/" + scanner

        for root,dirs,files in os.walk(scanner_path):

            for file in files:

                if file.endswith(".tif"):

                    path=os.path.join(root,file)

                    img=cv2.imread(path,0)

                    if img is None:
                        continue

                    blur=cv2.GaussianBlur(img,(5,5),0)

                    residual=img-blur

                    residual=cv2.resize(residual,(128,128))

                    # Statistical features
                    mean = np.mean(residual)
                    std = np.std(residual)
                    var = np.var(residual)

                    # Histogram features
                    hist = cv2.calcHist([residual],[0],None,[32],[0,256])
                    hist = hist.flatten()

                    # Final feature vector
                    feature = np.concatenate(([mean,std,var],hist))

                    X.append(feature)

                    y.append(scanner)


X=np.array(X)
y=np.array(y)

print("Features Shape:",X.shape)

from sklearn.metrics import accuracy_score, confusion_matrix, classification_report

print("Training Model...")

scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)

model = SVC(kernel='linear', probability=True)

model.fit(X_scaled, y)

# 🔥 Prediction
pred = model.predict(X_scaled)

# 🔥 Accuracy
accuracy = accuracy_score(y, pred)
print("Accuracy:", accuracy)

# 🔥 Confusion Matrix
print("\nConfusion Matrix:")
print(confusion_matrix(y, pred))

# 🔥 F1-score + Precision + Recall ⭐
print("\nClassification Report:")
print(classification_report(y, pred))

# Save model
pickle.dump(model, open("model.pkl", "wb"))
pickle.dump(scaler, open("scaler.pkl", "wb"))

print("Model Saved")