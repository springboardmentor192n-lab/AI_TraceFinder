# TraceFinder - AI Document Forensic Intelligence

Advanced AI-powered document forensic analysis for scanner identification and tampering detection.

## 🚀 Quick Start

### Streamlit App (Python Backend)
```bash
pip install -r requirements.txt
streamlit run forensics_app.py
```

### React App (Frontend)
```bash
cd react-app
npm install
npm start
```

## 📁 Project Structure

```
TraceFinder/
├── forensics_app.py          # Main Streamlit application
├── requirements.txt           # Python dependencies
├── react-app/              # React frontend
│   ├── src/
│   │   ├── components/
│   │   └── pages/
│   └── package.json
├── artifacts/               # ML models and data
└── .streamlit/             # Streamlit configuration
```

## 🔬 Features

- **Scanner Identification**: Identify scanner brand/model with 95%+ accuracy
- **Tampering Detection**: Advanced forgery detection using ML
- **Multi-Page React UI**: Professional dashboard with charts
- **Authentication**: Login/Signup with Google/Facebook OAuth
- **Export**: PDF reports and JSON data export
- **History**: Searchable analysis history with filters

## 🌐 Access

- **Streamlit App**: http://localhost:8501
- **React App**: http://localhost:3000

## 📊 Supported Scanners

- Canon LiDE 120, CanoScan 9000F
- HP ScanJet Pro 2500
- Epson Perfection V39, V550
- And more...

## 🤖 Technology Stack

- **Backend**: Python, Streamlit, TensorFlow, OpenCV
- **Frontend**: React, Recharts, Lucide Icons
- **ML**: CNN + SVM Hybrid Architecture
- **Features**: PRNU Analysis, Noise Pattern Detection

## 📄 License

MIT License - see LICENSE file for details.
