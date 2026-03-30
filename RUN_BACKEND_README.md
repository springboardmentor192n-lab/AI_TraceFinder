# Running AI TraceFinder Backend

## Quick Start Options

### Option 1: Using Ctrl+Shift+B (VS Code Build Task) ⭐ **RECOMMENDED**
1. Open the project in VS Code
2. Press `Ctrl+Shift+B` (or `Cmd+Shift+B` on Mac)
3. Select "Run AI TraceFinder Backend"
4. The server will start on http://localhost:10000

### Option 2: Using Run Script
- **Windows Batch**: Double-click `run_backend.bat`
- **Windows PowerShell**: Run `.\run_backend.ps1`
- **Unix/Linux/Mac**: Run `./run_unix.sh`

### Option 3: Using VS Code Launch Configuration (F5)
1. Open `backend/app.py`
2. Press `F5` to start debugging
3. Choose "AI TraceFinder Backend (Port 10000)" from the dropdown

### Option 4: Manual Command Line
```bash
# Activate virtual environment (Windows)
venv\Scripts\activate.bat

# Or on PowerShell
venv\Scripts\Activate.ps1

# Or on Mac/Linux
source venv/bin/activate

# Run the backend
python backend/app.py
```

## Available Tasks in VS Code

Press `Ctrl+Shift+B` to access these tasks:

| Task | Shortcut | Description |
|------|----------|-------------|
| **Run AI TraceFinder Backend** | `Ctrl+Shift+B` | Start the Flask server on port 10000 (Default Build Task) |
| Open App in Browser | Via Command Palette | Open http://localhost:10000 in default browser |
| Install Dependencies | Via Command Palette | Install required Python packages |
| Check System Setup | Via Command Palette | Verify all system requirements are met |
| Run Tests | Via Command Palette | Run backend tests |

## Accessing the Application

Once the backend is running:

- **Web Interface**: http://localhost:10000
- **API Docs (HTML)**: http://localhost:10000/api/docs-html
- **API Docs (JSON)**: http://localhost:10000/api/docs
- **Health Check**: http://localhost:10000/api/health

## Troubleshooting

### Port Already in Use
If port 10000 is already in use:
```bash
# Find process using port 10000 (Windows)
netstat -ano | findstr :10000

# Kill the process (Windows)
taskkill /PID <PID> /F
```

### Virtual Environment Issues
```bash
# Recreate virtual environment
rmdir /s venv
python -m venv venv
venv\Scripts\activate.bat
pip install -r requirements.txt
```

### Module Import Errors
```bash
# Update pip and reinstall dependencies
python -m pip install --upgrade pip
pip install -r requirements.txt
```

## Configuration

- **Backend Port**: 10000 (configured in `backend/app.py`)
- **Frontend Path**: `frontend/` directory
- **Upload Folder**: `backend/uploads/`
- **Max File Size**: 50MB
- **Auto-cleanup**: Files older than 24 hours are automatically removed

## Development

For development mode with auto-reload:
```bash
export FLASK_ENV=development
export FLASK_DEBUG=1
python backend/app.py
```

Or use the VS Code Launch Configuration which sets these automatically.
