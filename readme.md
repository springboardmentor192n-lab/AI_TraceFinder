
# TraceFinder - Forensic Scanner Identification System

![TraceFinder Banner](https://img.shields.io/badge/Project-TraceFinder-red?style=for-the-badge&logo=react)
![Python](https://img.shields.io/badge/Python-3.10-blue?style=flat-square&logo=python)
![PyTorch](https://img.shields.io/badge/PyTorch-DeepLearning-orange?style=flat-square&logo=pytorch)
![React](https://img.shields.io/badge/React-18+-cyan?style=flat-square&logo=react)

**TraceFinder** is an advanced forensic tool designed to identify the source scanner device used to create a digital document. By analyzing unique noise patterns (PRNU) and artifacts left by scanner sensors, the system uses a Deep Learning model (CNN) to classify documents with high accuracy.

---

## 📺 Working Video
[Click here to watch the Working Video Demo](https://drive.google.com/drive/u/0/folders/1aSosFEQcT3NMq7hwgK8l7kmMVLYE5ZX9)

---

## 🚀 Key Features

- **Scanner Identification:** Identifies the brand/model of the scanner used to scan a document.
- **Noise Analysis:** Extracts and analyzes residual noise patterns (PRNU) from images to find unique device fingerprints.
- **PDF & Image Support:** Processes standard image formats (JPG, PNG) and PDF documents directly.
- **Interactive Dashboard:**
    - Real-time confidence distribution charts (Top 5 predictions).
    - Feature quality metrics (PRNU, Noise Level, Image Quality).
    - Metadata status verification.
- **Reporting & History:**
    - **PDF Report Generation:** Download detailed forensic reports including tables and metrics.
    - **JSON Export:** Export raw analysis data.
    - **Analysis History:** Stores past analyses locally for easy review (stored in LocalStorage).
- **Modern UI:** Built with React & Tailwind CSS for a responsive, professional dark-mode experience.

---

## 🛠 Tech Stack

**Backend:**
- **Python 3.10**
- **Flask** (Web Server & API)
- **PyTorch** (Deep Learning Model)
- **OpenCV** (Image Processing & Residual Extraction)
- **pdf2image** (PDF Handling)

**Frontend:**
- **React 18+** (Vite)
- **Tailwind CSS** (Styling)
- **Chart.js** (Data Visualization)
- **jsPDF** (Report Generation)
- **React Router** (Navigation)

---

## 📁 Project Structure

```text
TraceFinder/
├── backend/
│   ├── model/
│   │   ├── deep_scanner_cnn.pth    # Trained Model Weights
│   │   └── label_map_cnn.npy       # Label Mappings
│   ├── uploads/                    # Temporary storage (auto-cleaned)
│   ├── app.py                      # Flask Server Entry Point
│   ├── scanner_pipeline.py         # Core ML Logic & Preprocessing
│   └── requirements.txt            # Python Dependencies
│
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   └── Navbar.jsx
│   │   ├── pages/
│   │   │   ├── Dashboard.jsx
│   │   │   ├── History.jsx
│   │   │   └── About.jsx
│   │   ├── App.jsx
│   │   ├── main.jsx
│   │   └── main.css
│   ├── index.html
│   └── package.json
│
└── README.md
```

---

## ⚙️ Setup & Installation

### Prerequisites
- **Python 3.10** installed.
- **Node.js** (v16+) installed.
- **Poppler** (Required for PDF processing on Windows).
    1. Download the latest binary: [Poppler for Windows](https://github.com/oschwartz10612/poppler-windows/releases).
    2. Extract it (e.g., to `C:\Program Files\poppler`).
    3. Add the `bin` folder path (e.g., `C:\Program Files\poppler\Library\bin`) to your Windows **Environment Variables** -> **Path**.

### 1. Backend Setup

1.  **Navigate to the backend folder:**
    ```bash
    cd backend
    ```

2.  **Create and activate a virtual environment:**
    ```bash
    python -m venv venv
    # Windows
    venv\Scripts\activate
    # Mac/Linux
    source venv/bin/activate
    ```

3.  **Install Dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Add Model Files:**
    *   Place your trained model files (`deep_scanner_cnn.pth` and `label_map_cnn.npy`) inside `backend/model/`.

5.  **Run the Server:**
    ```bash
    python app.py
    ```
    The server will start at `http://127.0.0.1:5000`.

### 2. Frontend Setup

1.  **Navigate to the frontend folder:**
    ```bash
    cd frontend
    ```

2.  **Install Dependencies:**
    ```bash
    npm install
    ```

3.  **Run the Development Server:**
    ```bash
    npm run dev
    ```
    Open the provided link (usually [http://localhost:5173](http://localhost:5173)) in your browser.

---

## 📝 Usage

1.  **Dashboard:** Open the web application.
2.  **Upload:** Drag and drop or click to upload a scanned document (Image or PDF).
3.  **Analyze:** Click "Run Analysis" to process the document.
4.  **Results:** View the predicted scanner, confidence score, and feature metrics.
5.  **Report:** Click "PDF Report" to download a detailed forensic report or "Export JSON" for raw data.
6.  **History:** Navigate to the "History" tab to view past analyses.

---

## 🧠 Model Architecture

The project uses a custom **DeepScannerCNN**:
-   **Input:** 32x32 Grayscale Noise Residual (Image - Denoised Image).
-   **Architecture:** 3 Convolutional Blocks (Conv2d + BatchNorm + ReLU + MaxPool).
-   **Classifier:** Fully Connected Layers with Dropout.
-   **Output:** Softmax probabilities for 44+ scanner classes.

---

## 📄 License
This project was created for educational and forensic research purposes.

---

## 👤 Author
**Athulya km**
```