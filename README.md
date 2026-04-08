# TraceFinder - AI Document Forensic Intelligence

Advanced AI-powered document forensic analysis pipeline for scanner hardware identification and digital tampering detection natively deployed via an enterprise dashboard.

## 🚀 Quick Start

Ensure you have your dependencies successfully installed to launch the AI dashboard:

```bash
pip install -r requirements.txt
cd app
python -m streamlit run app.py
```

## 📁 Project Structure

```
TraceFinder_Final/
├── app/
│   └── app.py                  # Main Streamlit Enterprise Dashboard Interface
├── model/  
│   └── cnn_model.py            # Neural Network Architecture (Pretrained ResNet18 adapted for 1-Channel)
├── dataset_loader.py           # I/O script mapping scanner identity patches (128x128)
├── tamper_loader.py            # I/O script mapping manipulation anomaly datasets
├── train.py                    # Scanner source-identification ML training loop
├── train_tamper.py             # Feature tampering classification training loop
├── model.pth                   # Frozen neural weights for Scanner Classification
├── tamper_model.pth            # Frozen neural weights for Forgery Classification
└── requirements.txt            # Python deep learning dependencies
```

## 🔬 Features & Workflow

- **Scanner Hardware Identification**: Extracts micro-noise residuals natively printed by specific hardware to identify the exact scanner brand/model.
- **Patch-Level Tampering Detection**: Advanced digital forgery detection algorithm detecting copy-move, splicing, and local retouching anomalies across scanned documentation. 
- **Enterprise Dashboard**: A custom-styled, strictly professional multi-page UI handling real-time File Uploads bridging directly into PyTorch predictions.
- **Dynamic Spectral Mapping**: Generates active Pseudo-Heatmaps (e.g., Built-In Spectral Analysis, Noise Variance Enhancement) upon image scanning inside the dashboard.
- **Bulk Analytics Pipeline**: Handles simultaneous parsing and automated classification matrix metrics for batch uploads.

## 🌐 Access

- **Live Deployment Link**: http://localhost:8503  *(Replace with actual Cloud Deployment Domain before final submission)*

## 📊 Supported Scanners

The Neural Network accurately differentiates traces spanning key hardware components including:
- Canon LiDE 120, CanoScan 9000F, CanoScan 220
- Epson Perfection V39, V370, V550
- Generic HP Scanners

## 🤖 Technology Stack

- **Backend / Machine Learning**: Python, PyTorch, OpenCV, Scikit-Learn
- **Core ML Architecture**: Transfer Learning (Feature-extracted `ResNet18` collapsed onto 1-Channel CNN logic)
- **Frontend / Interface Engine**: Streamlit mapped with dynamic customized CSS properties rendering Neumorphic formatting.

## 📈 Demonstration Outputs

To view the exact performance, output graphics, and interface execution of the model, **just look the `results` folder** directly inside this repository!

## 📄 License

MIT License - see LICENSE file for details.
