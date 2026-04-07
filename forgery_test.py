import cv2
import matplotlib.pyplot as plt

# Load image (use any official or wikipedia image for now)
path = "Dataset/Official/Canon9000-1/300.tif"

img = cv2.imread(path,0)

# Residual extraction
blur = cv2.GaussianBlur(img,(5,5),0)

residual = img - blur

# Absolute value
residual = cv2.convertScaleAbs(residual)

# Threshold to detect abnormal regions
_, thresh = cv2.threshold(residual,30,255,cv2.THRESH_BINARY)

# Show results
plt.figure(figsize=(10,5))

plt.subplot(1,3,1)
plt.title("Original")
plt.imshow(img,cmap='gray')

plt.subplot(1,3,2)
plt.title("Residual")
plt.imshow(residual,cmap='gray')

plt.subplot(1,3,3)
plt.title("Forgery Detection")
plt.imshow(thresh,cmap='gray')

plt.show()