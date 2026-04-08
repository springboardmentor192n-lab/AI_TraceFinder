# AI_TRACEFINDER: Document Forensics Engine

**AI_TRACEFINDER** is an advanced, enterprise-grade AI pipeline designed for physical document forensics. The system functions as a high-fidelity anomaly scanner capable of determining the hardware origin (scanner source identity) of a specific document, while simultaneously inspecting images at the patch level to detect digital tampering or forgery manipulations.

---

### Workflow Architecture
The system follows a streamlined document inspection pipeline:
1. **Upload & Preprocessing:** Users submit `.png`, `.tif`, or `.jpg` documents via the Streamlit web dashboard.
2. **Patch Extraction:** The internal scripts decompose high-resolution images into structured `128x128` patches required by the convolution filters.
3. **Deep Learning Inference:** The patches undergo dual-inference through the AI PyTorch engines:
   - **Scanner Profiler:** Extracts hardware-level noise characteristics to identify the scanner brand/model.
   - **Anomaly Detector:** Scans edges and internal residual noise to check for digital splicing, copy-moving, or localized retouching variants.
4. **Dashboard Execution:** The system parses output probability matrices to render clear predictions, confidence scores, and outputs custom Pseudo-Heatmap filters (such as Noise Residual and Spectral analysis maps) natively inside the UI.

---

### Project Files & Directory Structure

*   `app/app.py`: The main frontend engine. Built on Streamlit with comprehensive UI designs, it manages interactive end-user uploading (Single & Batch pipelines), triggers neural inference, and visually handles data presentation.
*   `model/cnn_model.py`: Architecturally houses the deep learning structure that establishes the core `CNN` module mapped over the custom ResNet18 backbone. 
*   `train.py`: The PyTorch training loop algorithm utilized to train our hardware Identification model on standard noise data (`model.pth`).
*   `train_tamper.py`: The targeted classification training script configured specifically to teach the engine structural manipulations utilizing optimized weight decay (`tamper_model.pth`).
*   `dataset_loader.py` & `tamper_loader.py`: Specialized system utility files focusing on I/O operations, dataset structure mapping, and random geometric data slicing so the models correctly learn patch features instead of memorizing native sizes.
*   `model.pth` & `tamper_model.pth`: The final frozen state-dictionary artifacts holding the mathematical weights resulting from the deep learning sessions.

---

### Model Architecture Details
To ensure extremely resilient accuracy over complex grayscale scanner noise, we successfully upgraded the core engine to **Transfer Learning**.
*   **Base Network**: We integrated the heavily utilized `ResNet18` deep learning model.
*   **1-Channel Augmentation**: Standard ResNet dictates a 3-channel RGB assumption. To retain the highly-functional pre-trained edges without causing structural failure, we initialized the `conv1` layer dynamically by mathematically collapsing the three pre-trained channels directly into our 1-channel dimension. This guarantees rapid convergence limits overfitting without discarding critical early-layer mathematical mappings.

---

### Live Deployment
🚀 **[View Live Dashboard Deployment Here]($\{INSERT_DEPLOYMENT_LINK_HERE\})**

### Demonstration & Outputs

To view the output images and visual demonstration of the Dashboard, **just look in the `results` folder** inside this repository!
