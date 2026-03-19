# AI TraceFinder - Quick Start Guide

## ⚡ 5-Minute Setup

### Step 1: Download & Extract
- Extract the `AI_TraceFinder_Complete` folder to your desired location

### Step 2: Run Setup

**Windows:**
```powershell
# Option 1: Double-click
setup_windows.bat

# Option 2: Command Prompt in folder
setup_windows.bat
```

**macOS/Linux:**
```bash
# Make executable
chmod +x setup_unix.sh

# Run setup
./setup_unix.sh
```

### Step 3: Start Server

**Windows:**
```powershell
# Double-click or run:
run_windows.bat

# Manual start:
venv\Scripts\activate
cd backend
python app.py
```

**macOS/Linux:**
```bash
# Run the script:
./run_unix.sh

# Manual start:
source venv/bin/activate
cd backend
python app.py
```

### Step 4: Open Browser
- Navigate to: **http://localhost:5000**
- Start analyzing images!

---

## 📁 Project Structure

```
AI_TraceFinder_Complete/
│
├─ backend/
│  ├─ app.py                      # Flask application
│  ├─ image_forensics.py          # Core forensics engine
│  ├─ config.py                   # Configuration settings
│  └─ uploads/                    # Temp image storage
│
├─ frontend/
│  ├─ templates/
│  │  └─ index.html               # Web interface
│  └─ static/
│     ├─ styles.css               # Styles
│     └─ script.js                # Frontend logic
│
├─ models/                         # Pre-trained models
├─ data/                          # Sample data
├─ docs/                          # Documentation
│
├─ requirements.txt               # Dependencies
├─ setup_windows.bat              # Windows setup
├─ setup_unix.sh                  # Unix/Linux setup
├─ run_windows.bat                # Windows run script
├─ run_unix.sh                    # Unix/Linux run script
└─ README.md                      # Full documentation
```

---

## 🚀 Commands Reference

### Virtual Environment
```bash
# Windows
venv\Scripts\activate
deactivate

# macOS/Linux
source venv/bin/activate
deactivate
```

### Backend
```bash
cd backend
python app.py              # Start server
python app.py --debug     # Debug mode (auto-reload)
```

### Dependencies
```bash
pip install -r requirements.txt      # Install all
pip list                             # Show installed
pip install --upgrade package_name   # Update package
```

---

## 🎯 Common Tasks

### Upload Test Images
1. Go to http://localhost:5000
2. Drag image into upload area
3. Click "Analyze Image"

### Batch Analysis
1. Click "Batch Upload" tab
2. Select multiple images (up to 10)
3. Click "Analyze All"
4. View results table

### Get API Documentation
1. Click "API" in header
2. View available endpoints
3. Test with curl/Python

### Download Report
1. Click "Download Report" button
2. JSON file saves automatically
3. Open with text editor to view

---

## ⚙️ Configuration

Edit `backend/config.py` to change:

- **MAX_FILE_SIZE**: Upload limit
- **IMAGE_SIZE**: Processing resolution
- **PORT**: Server port (default: 5000)
- **LOG_LEVEL**: Verbosity

Example:
```python
MAX_CONTENT_LENGTH = 100 * 1024 * 1024  # Change 50MB to 100MB
PORT = 5001  # Change port
```

---

## 🆘 Troubleshooting

### "Port 5000 in use"
```bash
# Mac/Linux: Find process
lsof -i :5000
kill -9 <PID>

# Windows: Find process
netstat -ano | findstr :5000
taskkill /PID <PID> /F
```

### "Module not found"
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### Slow Performance
- Close unnecessary programs
- Check system RAM usage
- Use images < 10MB

---

## 📱 API Quick Test

### cURL (Terminal)
```bash
curl -X POST http://localhost:5000/api/analyze \
  -F "image=@test.jpg"
```

### Python
```python
import requests

with open('test.jpg', 'rb') as f:
    r = requests.post('http://localhost:5000/api/analyze', files={'image': f})
    print(r.json())
```

### JavaScript
```javascript
const formData = new FormData();
formData.append('image', imageFile);

fetch('/api/analyze', {
  method: 'POST',
  body: formData
}).then(r => r.json()).then(data => console.log(data));
```

---

## 🔗 Useful Links

- **Web UI**: http://localhost:5000
- **API Docs**: http://localhost:5000/api/docs
- **Health Check**: http://localhost:5000/api/health
- **GitHub**: [Repository Link]
- **Issues**: [Issues Page]

---

## 📚 Learn More

See `README.md` for:
- Detailed API documentation
- Technical architecture
- Feature descriptions
- Contributing guidelines
- Troubleshooting guide

---

**Questions?** Check README.md or open an issue!

**Happy Analyzing!** 🔍✨
