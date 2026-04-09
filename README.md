# TraceFinder - Forensic Scanner Identification

TraceFinder is a digital forensics project that identifies which scanner was used to scan a document.

When a document is scanned, the scanner leaves tiny hidden noise patterns in the image. These patterns are unique because every scanner has small hardware imperfections, such as sensor defects, dust, and optical variations.

TraceFinder analyzes those scanner fingerprints to determine:

- The scanner brand, such as Canon, Epson, HP, or Brother
- The scanner model
- The likely source device instance when enough reference data is available

## Core Idea

Just like cameras leave digital fingerprints and printers leave toner patterns, scanners also leave unique image signatures.

TraceFinder extracts these signatures and uses scanner-image features to identify the source scanner. The backend first tries to use the trained `backend/scanner_model.pkl`. If the model is unavailable or the prediction confidence is low, it uses reference feature matching from `backend/sample_dataset/`.

## Quick Start

Install dependencies from the project root:

```bash
pip install -r requirements.txt
```

Start the Flask backend:

```bash
python backend/app.py
```

Then open:

```text
http://localhost:5050
```

### Windows PowerShell

If you are using a local virtual environment:

```powershell
cd tracefinder
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python backend\app.py
```

If you already created a local environment named `.venv-local`, you can use:

```powershell
.\.venv-local\Scripts\Activate.ps1
pip install -r requirements.txt
python backend\app.py
```

Then open:

```text
http://localhost:5050
```

## Features

- Scanner identification from uploaded scanned documents
- Tampering detection using noise, edge, JPEG artifact, and metadata checks
- Document comparison for likely same-scanner origin
- Batch processing for multiple documents
- Browser-side case history using local storage
- JSON export and printable report output

## Project Structure

```text
tracefinder/
|-- README.md
|-- requirements.txt            # Root dependency installer
|-- .gitignore
|-- frontend/
|   |-- index.html              # Main web interface
|   `-- assets/
|       |-- css/
|       |   `-- styles.css
|       `-- js/
|           `-- app.js
`-- backend/
    |-- app.py                  # Flask API and frontend server
    |-- train_model.py          # Rebuilds scanner_model.pkl from sample data
    |-- requirements.txt        # Backend Python dependencies
    |-- scanner_model.pkl       # Scanner model artifact
    `-- sample_dataset/          # Local reference samples, ignored by Git
        |-- Brother_MFC_L2710DW/
        |-- Canon_CanoScan_9000F/
        |-- Epson_Perfection_V600/
        `-- HP_OfficeJet_Pro_8710/
```

## API Endpoints

- `GET /api/health` - Health check
- `GET /api/model-info` - Trained model metadata
- `GET /api/test-image` - Generate a test image
- `POST /api/analyze` - Scanner identification
- `POST /api/tampering` - Tampering detection
- `POST /api/compare` - Document comparison

## Requirements

- Python 3.7+
- Flask
- Flask-CORS
- OpenCV
- NumPy
- Pillow
- Modern web browser

Install dependencies:

```bash
pip install -r requirements.txt
```

TraceFinder uses `scikit-learn` and `backend/scanner_model.pkl` for trained-model scanner identification. If the model cannot be loaded or returns a low-confidence prediction, the app can still identify scanners by matching extracted features against reference samples in `backend/sample_dataset/`

## Retrain the Scanner Model

If the feature extractor changes or new reference samples are added, rebuild the model:


#Demo Video Link
https://drive.google.com/file/d/1NkMfBG2F_37NpnsuScKc1srJRncRiHkG/view?usp=sharing
## This is the drive link for the Demo video

```bash
python backend/train_model.py
```
