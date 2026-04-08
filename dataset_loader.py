import os, cv2, numpy as np

def extract_patches(img, size=128):
    import random
    patch_size = size
    h, w = img.shape
    patches = []
    
    if h >= patch_size and w >= patch_size:
        for _ in range(30): # Extract 30 random patches per image
            i = random.randint(0, h - patch_size)
            j = random.randint(0, w - patch_size)
            patches.append(img[i:i+patch_size, j:j+patch_size])
    return patches

def load_dataset(path):
    X, y = [], []
    classes = sorted(os.listdir(path))

    print("Classes:", classes)

    for i, c in enumerate(classes):
        folder = os.path.join(path, c)

        for f in os.listdir(folder):
            img_path = os.path.join(folder, f)
            img = cv2.imread(img_path, 0)

            if img is None:
                continue

            patches = extract_patches(img)

            for p in patches:
                p = cv2.resize(p, (128, 128))
                X.append(p / 255.0)
                y.append(i)

    return np.array(X), np.array(y), classes