import streamlit as st
import cv2
import numpy as np
import pickle
from pdf2image import convert_from_bytes
import pandas as pd
import os

log_file = "log.csv"

if not os.path.exists(log_file):
    df = pd.DataFrame(columns=["File Name","Prediction","Confidence"])
    df.to_csv(log_file,index=False)


# ----------------------------
# Page Setup
# ----------------------------

st.set_page_config(page_title="TraceFinder",
                   layout="centered")

st.title("TraceFinder - Document Forensics System")

st.write("Upload Image or PDF to detect scanner and forgery")

# ----------------------------
# Load Model + Scaler
# ----------------------------

model = pickle.load(open("model.pkl","rb"))
scaler = pickle.load(open("scaler.pkl","rb"))

# ----------------------------
# Upload File
# ----------------------------

uploaded_file = st.file_uploader(
    "Upload Image or PDF",
    type=["png","jpg","jpeg","tif","pdf"]
)

# ----------------------------
# Process File
# ----------------------------

if uploaded_file is not None:

    # ---------------- PDF ----------------
    if uploaded_file.type == "application/pdf":

        pages = convert_from_bytes(
            uploaded_file.read(),
            poppler_path=r"C:\poppler\Library\bin"
        )

        img = np.array(pages[0])

        img = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)

    # ---------------- IMAGE ----------------
    else:

        file_bytes = np.asarray(
            bytearray(uploaded_file.read()),
            dtype=np.uint8
        )

        img = cv2.imdecode(file_bytes,0)

    # Show image
    st.subheader("Uploaded Document")
    st.image(img, width=400)

    # ---------------- ANALYZE BUTTON ----------------
    if st.button("Analyze Document"):

        # ---------------- Residual ----------------
        blur = cv2.GaussianBlur(img,(5,5),0)
        residual = img - blur

        # ---------------- DIGITAL CHECK ----------------
        std_value = np.std(residual)

        if std_value < 2:

            st.subheader("Scanner Detection")
            st.warning("Digital Document (No Scanner Detected)")

        else:

            # ---------------- FEATURE EXTRACTION ----------------
            residual = cv2.resize(residual,(128,128))

            mean = np.mean(residual)
            std = np.std(residual)
            var = np.var(residual)

            hist = cv2.calcHist([residual],[0],None,[32],[0,256])
            hist = hist.flatten()

            feature = np.concatenate(([mean,std,var],hist))
            feature = feature.reshape(1,-1)

            feature = scaler.transform(feature)

            # ---------------- PREDICTION ----------------
            prediction = model.predict(feature)

            probs = model.predict_proba(feature)[0]

            confidence = np.max(probs) * 100

            st.success(f"Predicted Scanner: {prediction}")

            st.info(f"Confidence: {confidence:.2f}%")
            
            new_entry = {
            "File Name": uploaded_file.name,
            "Prediction": prediction,
            "Confidence": round(confidence,2)
            }

            df = pd.read_csv(log_file)

            df = pd.concat([df, pd.DataFrame([new_entry])], ignore_index=True)

            df.to_csv(log_file, index=False)
            
            
            st.subheader("Scanner Detected")
            
            st.subheader("Prediction Log")

            df = pd.read_csv(log_file)

            st.dataframe(df)
            
            
            st.download_button(
            label="Download Log as CSV",
            data=df.to_csv(index=False),
            file_name="prediction_log.csv",
            mime="text/csv"
            )

        # ---------------- FORGERY DETECTION ----------------

        residual_abs = cv2.convertScaleAbs(residual)

        _, thresh = cv2.threshold(residual_abs,30,255,cv2.THRESH_BINARY)

        white_pixels = np.sum(thresh > 0)

        st.subheader("Forgery Detection")

        if white_pixels > 5000:

            st.error("Forgery Detected")

        else:

            st.success("No Forgery Detected")

        # Show detection map
        st.subheader("Forgery Map")

        st.image(thresh, width=400)