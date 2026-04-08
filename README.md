# AI_TRACEFINDER : Advanced Document Forensics Engine

**AI_TRACEFINDER** is an enterprise-grade document forensics pipeline combining deep learning with a custom, high-performance web dashboard. It acts as an end-to-end anomalies scanner capable of identifying the hardware source of scanned documents and flagging patch-level forgery manipulation.

---

### Project Overview
The pipeline solves physical document tracing and manipulation tracking using the following comprehensive workflow:
1. **AI Neural Network Upgrades**: The core architecture relies on an advanced Transfer Learning pipeline built off a PyTorch `ResNet18` model. The pretrained backbone natively processes complex grayscale arrays, aggressively out-performing simpler CNN matrices while eliminating extreme overfitting on small batch variants via robust learning rate optimization and structural regularization.
2. **Dashboard UI Refactoring**: The user interface was completely overhauled using `Streamlit`. Reconstructed away from a minimal web framework representation into an immersive **Enterprise Dashboard**. It integrates professional visual themes (Neumorphic shading, conditional progress bars, status diagnostics pane) and distinct Navigation pipelines targeting "Single Document" and "Batch Analysis" modules.
3. **Forensic Inference Pipeline**: Custom hooks directly resize `.pdf`, `.tif`, and native `.jpg` input variants to perfectly match the internal `128x128` convolution filters alongside generating high-fidelity evaluation metrics and visual Pseudo-Heatmaps (e.g., Noise Residual, Enhanced Edge Mapping, Spectral Outputs).

### Live Deployment
🚀 **[View Live Dashboard Deployment Here]($\{INSERT_DEPLOYMENT_LINK_HERE\})**

### Demonstration
*Note: Replace these placeholders before submittal by attaching the actual screen recordings generated.*

#### Screenshots
- ![Dashboard Execution](docs/demo1.jpg)
- ![Batch Output](docs/demo2.jpg)

#### Demo Video
- [Watch Full User Flow Interface Demo](docs/demo_video.mp4)

---
*Created in collaboration for the 2026 Machine Learning Application Submittal.*
