import streamlit as st
import tensorflow as tf
import numpy as np
import cv2
import pandas as pd
import os
from datetime import datetime

# Load trained model
model = tf.keras.models.load_model("/content/drive/MyDrive/scanner_cnn_model.keras")

class_labels = ['Canon120-2','Canon220','Canon9000-1','Canon9000-2',
                'EpsonV370-2','EpsonV39-1','EpsonV39-2','EpsonV550','HP']

st.title("TraceFinder - AI Scanner Identification")

st.write("Upload a scanned document. The system analyzes scanner fingerprint noise patterns.")

uploaded_file = st.file_uploader(
    "Upload scanned image",
    type=["jpg","jpeg","png","tif","tiff"]
)

if uploaded_file is not None:

    file_bytes = np.asarray(bytearray(uploaded_file.read()), dtype=np.uint8)
    img_original = cv2.imdecode(file_bytes, cv2.IMREAD_GRAYSCALE)

    st.subheader("Uploaded Image")
    st.image(img_original, use_column_width=True)

    # Resize for model
    img = cv2.resize(img_original,(256,256))
    img = img / 255.0
    img = np.expand_dims(img,-1)
    img = np.expand_dims(img,0)

    # ---------- Residual Noise ----------
    st.subheader("Residual Noise Pattern")

    blur = cv2.GaussianBlur(img_original,(5,5),0)
    residual = cv2.subtract(img_original,blur)

    st.image(residual,use_column_width=True)

    # ---------- Frequency Domain ----------
    st.subheader("Frequency Spectrum")

    f = np.fft.fft2(img_original)
    fshift = np.fft.fftshift(f)
    magnitude = np.log(np.abs(fshift)+1)

    st.image(magnitude,use_column_width=True)

    # ---------- Prediction ----------
    prediction = model.predict(img)

    pred_index = np.argmax(prediction)
    confidence = float(np.max(prediction))

    predicted_class = class_labels[pred_index]

    st.subheader("Prediction Result")

    st.success(f"Predicted Scanner: {predicted_class}")

    st.info(f"Confidence Score: {confidence*100:.2f}%")

    # ---------- Logging ----------
    log_data = {
        "Time": datetime.now(),
        "Prediction": predicted_class,
        "Confidence": confidence
    }

    log_df = pd.DataFrame([log_data])

    if os.path.exists("logs.csv"):
        log_df.to_csv("logs.csv", mode='a', header=False, index=False)
    else:
        log_df.to_csv("logs.csv", index=False)

    st.success("Prediction logged successfully.")
