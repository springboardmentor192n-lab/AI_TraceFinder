# TraceFinder Backend Enhancement Guide

## 🚀 New Features Added

### 1. **User Authentication System**
- ✅ User registration and login endpoints
- ✅ Password hashing with Werkzeug
- ✅ Flask-Login integration for session management
- ✅ Protected endpoints requiring authentication
- ✅ User profile and account information

### 2. **Database & Analysis History**
- ✅ SQLite database with SQLAlchemy ORM
- ✅ User model with email and username
- ✅ Analysis history tracking per user
- ✅ Statistics and aggregate queries
- ✅ Automatic cascading deletes

### 3. **Enhanced Error Handling & Logging**
- ✅ Comprehensive logging to `logs/api.log`
- ✅ File size validation (10 MB limit)
- ✅ Image format validation (.jpg, .png, .tiff)
- ✅ Detailed error messages with context
- ✅ Try-catch blocks in all feature extraction functions
- ✅ 404 and 500 error handlers

### 4. **New API Endpoints**

#### Authentication
- `POST /api/register` - Create new user account
- `POST /api/login` - User login with session
- `POST /api/logout` - Logout and clear session
- `GET /api/me` - Get current user info (protected)

#### Analysis
- `POST /analyze` - Analyze image with authentication
- `GET /api/history?limit=50` - Get user's analysis history (protected)
- `GET /api/analysis/<id>` - Get specific analysis result (protected)
- `GET /api/stats` - Get user statistics (protected)

#### System
- `GET /health` - Health check (no auth required)

---

## 📦 Installation & Setup

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

**New packages added:**
- Flask>=2.3.0
- Flask-CORS>=4.0.0
- Flask-Login>=0.6.0
- Flask-SQLAlchemy>=3.0.0
- Werkzeug>=2.3.0

### 2. Initialize Database
```bash
python backend/api.py
# The database is automatically created on first run
# Created file: tracefinder.db (SQLite)
```

### 3. Start the Backend Server
```bash
python backend/api.py
# Server runs on http://127.0.0.1:5000
# Database: tracefinder.db
# Logs: logs/api.log
```

### 4. Start the Frontend (in another terminal)
```bash
python -m http.server 8000
# Navigate to http://localhost:8000/tracefinder_auth.html
```

---

## 🧪 Testing

### Run Complete Test Suite
```bash
python test_api.py
```

This tests all endpoints in sequence:
1. ✓ Health check (no auth)
2. ✓ Unauthorized access protection
3. ✓ User registration
4. ✓ User login
5. ✓ Get current user
6. ✓ Multiple image analyses
7. ✓ Retrieve analysis history
8. ✓ Get user statistics
9. ✓ User logout

**Sample Output:**
```
======================================================================
TRACEFINDER API TEST SUITE
Server: http://127.0.0.1:5000
Started: 2026-04-02 10:30:15
======================================================================

Testing health check...
============================================================
Health Check Response
Status: 200
Response: {
  "model_ready": true,
  "missing_artifacts": [],
  "status": "ok",
  "timestamp": "2026-04-02T10:30:15.123456"
}
============================================================

✓ Health check passed
[... more tests ...]

======================================================================
TEST SUMMARY
======================================================================
✓ PASS: health_check
✓ PASS: unauthorized_protection
✓ PASS: register
✓ PASS: login
✓ PASS: get_me
✓ PASS: analyze_1
✓ PASS: analyze_2
✓ PASS: analyze_3
✓ PASS: history
✓ PASS: stats
✓ PASS: logout
======================================================================
Results: 11/11 tests passed
======================================================================
```

### Manual Testing with curl

```bash
# 1. Health check
curl http://127.0.0.1:5000/health

# 2. Register
curl -X POST http://127.0.0.1:5000/api/register \
  -H "Content-Type: application/json" \
  -d '{"username":"testuser","email":"test@example.com","password":"password123"}'

# 3. Login
curl -X POST http://127.0.0.1:5000/api/login \
  -H "Content-Type: application/json" \
  -c cookies.txt \
  -d '{"username":"testuser","password":"password123"}'

# 4. Get current user
curl http://127.0.0.1:5000/api/me \
  -b cookies.txt

# 5. Upload image (requires valid image file)
curl -X POST http://127.0.0.1:5000/analyze \
  -b cookies.txt \
  -F "file=@path/to/image.jpg"

# 6. Get history
curl http://127.0.0.1:5000/api/history?limit=10 \
  -b cookies.txt

# 7. Get stats
curl http://127.0.0.1:5000/api/stats \
  -b cookies.txt

# 8. Logout
curl -X POST http://127.0.0.1:5000/api/logout \
  -b cookies.txt
```

---

## 📝 API Documentation

### Registration
```
POST /api/register
Content-Type: application/json

{
  "username": "john_doe",      // 3+ characters
  "email": "john@example.com",
  "password": "secure123"       // 6+ characters
}

Response (201):
{
  "message": "user created successfully",
  "user": {
    "id": 1,
    "username": "john_doe",
    "email": "john@example.com",
    "created_at": "2026-04-02T10:30:15.123456"
  }
}
```

### Login
```
POST /api/login
Content-Type: application/json
Set-Cookie: session=...

{
  "username": "john_doe",
  "password": "secure123"
}

Response (200):
{
  "message": "logged in successfully",
  "user": { ... }
}
```

### Analyze Image
```
POST /analyze
Authorization: session cookie required
Content-Type: multipart/form-data

file: <image file>

Response (200):
{
  "analysis_id": 42,
  "tamper": 0.1234,
  "threshold": 0.5,
  "tampered": false,
  "patch_support": true,
  "top3": [
    ["Canon LiDE 120", 95.2],
    ["HP ScanJet Pro 2500", 87.3],
    ["Unknown Scanner", 42.1]
  ]
}
```

### Get History
```
GET /api/history?limit=50
Authorization: session cookie required

Response (200):
{
  "count": 5,
  "analyses": [
    {
      "id": 1,
      "filename": "document.jpg",
      "tampered": false,
      "tamper_score": 0.1234,
      "top_scanner": "Canon LiDE 120",
      "confidence": 95.2,
      "created_at": "2026-04-02T10:30:15.123456"
    },
    ...
  ]
}
```

### Get Statistics
```
GET /api/stats
Authorization: session cookie required

Response (200):
{
  "total_analyses": 25,
  "tampered_count": 8,
  "authentic_count": 17,
  "avg_tamper_score": 0.2456
}
```

---

## 🔒 Security Features

### Implemented
- ✅ Password hashing with Werkzeug
- ✅ Session-based authentication with Flask-Login
- ✅ CORS support with credentials
- ✅ File size validation
- ✅ File type validation
- ✅ User data isolation (users only access their own data)
- ✅ Error messages don't leak system details

### Recommendations for Production
- [ ] Use HTTPS/SSL certificates
- [ ] Implement rate limiting
- [ ] Add CSRF protection
- [ ] Rotate SECRET_KEY regularly
- [ ] Implement audit logging
- [ ] Add API key authentication for programmatic access
- [ ] Use environment variables for secrets

---

## 📊 Logging

### Log File
Location: `logs/api.log`

Includes:
- Authentication events (register, login, logout)
- Analysis submissions and results
- Error messages with full context
- Feature extraction details
- Database operations

### Log Examples
```
2026-04-02 10:30:15,234 - __main__ - INFO - User registered: john_doe
2026-04-02 10:31:22,456 - __main__ - INFO - User logged in: john_doe
2026-04-02 10:32:10,789 - __main__ - INFO - Analysis saved for user john_doe: document.jpg
2026-04-02 10:33:45,012 - __main__ - ERROR - Image load error: <details>
```

---

## 🖥️ Frontend Integration (tracefinder_auth.html)

### Features
- ✅ Login/Signup UI
- ✅ User authentication flow
- ✅ Protected analysis upload
- ✅ Real-time analysis results
- ✅ History page with statistics
- ✅ Error toasts and notifications
- ✅ Responsive design

### Usage Flow
1. User arrives at login page
2. Register or login
3. Upload document
4. Get real-time analysis results
5. View analysis history
6. Check statistics

### Authentication States
- **Logged Out**: Login/Signup pages, limited navigation
- **Logged In**: Home, History, About pages accessible

---

## 🐛 Troubleshooting

### "Cannot connect to API server"
```bash
# Make sure Flask is running:
python backend/api.py

# Check if port 5000 is in use:
lsof -i :5000  # macOS/Linux
netstat -an | find ":5000"  # Windows
```

### "Missing artifacts" error
Ensure all required model files exist in `artifacts/`:
- `scanner_hybrid.keras`
- `hybrid_label_encoder.pkl`
- `hybrid_feat_scaler.pkl`
- `scanner_fingerprints.pkl`
- `fp_keys.npy`

### "Database is locked" error
Close any other connections to `tracefinder.db` and restart the server.

### "Login fails" error
- Check username/password combination
- Verify user registration was successful
- Check logs in `logs/api.log`

---

## 📈 Performance Monitoring

### Check Model Loading Time
```python
# In logs, look for:
# "All artifacts loaded successfully"
```

### Monitor Inference Speed
Check logs for analysis completion timing:
```
...INFO - Inference complete: tampered=False, score=0.1234
```

### Database Query Performance
SQLAlchemy automatically handles query optimization.
For production, consider:
- Adding database indexes
- Implementing caching
- Query profiling

---

## 🔄 Backup & Recovery

### Backup User Data
```bash
cp tracefinder.db tracefinder.db.backup
cp -r logs/ logs.backup/
```

### Restore from Backup
```bash
cp tracefinder.db.backup tracefinder.db
cp -r logs.backup/ logs/
```

---

## 📚 Additional Resources

- Flask Documentation: https://flask.palletsprojects.com/
- Flask-Login: https://flask-login.readthedocs.io/
- SQLAlchemy: https://www.sqlalchemy.org/
- Chart.js: https://www.chartjs.org/

---

## 🎯 Next Steps

- [ ] Deploy to production server
- [ ] Add email verification for signup
- [ ] Implement password reset functionality
- [ ] Add API documentation with Swagger/OpenAPI
- [ ] Implement role-based access control (RBAC)
- [ ] Add batch processing capabilities
- [ ] Create mobile app frontend
- [ ] Setup CI/CD pipeline

---

## 📝 Version History

**v2.0.0** (2026-04-02)
- ✅ Added full authentication system
- ✅ Implemented database backend
- ✅ Enhanced error handling and logging
- ✅ Created comprehensive test suite
- ✅ Built modern authentication UI

**v1.0.0** (2026-03-30)
- Initial API release with basic /health and /analyze endpoints

---

## 👨‍💻 Support

For issues or questions:
1. Check logs in `logs/api.log`
2. Run `test_api.py` to verify setup
3. Review API documentation above
4. Check troubleshooting section

---

**Created**: April 2, 2026
**Last Updated**: April 2, 2026
