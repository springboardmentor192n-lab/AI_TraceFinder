import os, cv2, numpy as np

def load_tamper_dataset(base_path):
    X, y = [], []

    classes = ["Original", "Tampered"]

    for label, cls in enumerate(classes):
        folder = os.path.join(base_path, cls)

        for file in os.listdir(folder):
            img_path = os.path.join(folder, file)
            img = cv2.imread(img_path, 0)

            if img is None:
                continue

            img = cv2.resize(img, (128, 128))
            X.append(img / 255.0)
            y.append(label)

    return np.array(X), np.array(y), classes