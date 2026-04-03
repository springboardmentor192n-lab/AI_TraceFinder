"""Complete test walkthrough for TraceFinder"""

print("""
╔════════════════════════════════════════════════════════════════╗
║        TraceFinder - Complete Testing Guide                    ║
╚════════════════════════════════════════════════════════════════╝

🎯 TESTING SAMPLE OPTIONS:

Option 1: Generated Test Image (Quick Test)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  Run: generate_test_image.bat
  This creates: test_document.jpg
  Good for: Quick functionality test

Option 2: Use Existing Sample Files
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  Files available in project:
  ✓ fp_keys.npy (NumPy array)
  ✓ Any JPG/PNG/TIFF you have
  Good for: Real scanner fingerprint detection

Option 3: Download Real Scanner Images
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  Recommended sources:
  • Sample documents from your device
  • Scanned PDFs converted to images
  • Public test images from scanner datasets
  Good for: Accurate model testing


📋 COMPLETE TESTING WORKFLOW:

STEP 1: Generate Test Image
───────────────────────────
  cmd: generate_test_image.bat
  outputs: test_document.jpg in project folder


STEP 2: Open Browser
───────────────────────────
  Go to: http://127.0.0.1:8000/tracefinder_auth.html


STEP 3: Login
───────────────────────────
  Username: tejaswiputluri
  Password: Tejareddy@2006


STEP 4: Upload & Analyze
───────────────────────────
  1. Click "Select File to Upload"
  2. Choose test_document.jpg
  3. Click "Analyze Document"
  4. View results (top 3 scanner predictions, tampering score)


STEP 5: View Results
───────────────────────────
  Expected output:
  • Top 3 Scanner Predictions with confidence scores
  • Tampering Detection (Yes/No)
  • Tamper Score (0.0 - 1.0)
  • Analysis saved in history


📊 INTERPRETATION GUIDE:

Top 3 Scanner Predictions:
  Shows which scanner(s) the model thinks generated the image
  Example: Canon PowerShot: 95.2%, HP Scanner: 3.1%, Unknown: 1.7%

Tampering Detection:
  ✓ No = Image appears authentic
  ✗ Yes = Potential signs of tampering detected

Tamper Score (0.0 - 1.0):
  0.0 = Very confident image is authentic
  0.5 = Uncertain
  1.0 = High confidence image is tampered


🧪 AUTOMATED TEST COMMANDS:

Test with API directly:
────────────────────────
  python test_flow.py  (tests endpoints without auth)
  python diagnostic.py (tests with full auth flow)
  python create_user.bat (verify user creation)


📝 TROUBLESHOOTING:

If analysis fails:
  ✗ "endpoint not found" → Make sure logged in first
  ✗ "file too large" → Use images < 10MB
  ✗ "invalid format" → Use JPG, PNG, or TIFF only
  
If prediction seems wrong:
  • Model trained on specific scanner types
  • Image quality affects accuracy
  • Try different images for comparison


🚀 QUICK START (Copy & Paste):

  1. generate_test_image.bat
  2. Browser: http://127.0.0.1:8000/tracefinder_auth.html
  3. Login with credentials above
  4. Upload test_document.jpg
  5. Click Analyze
  6. Review results


✨ NEXT STEPS:

  • Test with multiple images
  • Check accuracy of predictions
  • View analysis history in dashboard
  • Report any incorrect predictions

════════════════════════════════════════════════════════════════
""")

import os

# List available test files
print("\n📦 Available Test Files in Project:")
print("─" * 60)
test_dir = r'C:\Users\tejap\Downloads\Trace_finder-20260402T041728Z-1-001\Trace_finder'

test_files = [
    'test_document.jpg',
    'fp_keys.npy',
    'test_flow.py',
    'diagnostic.py',
    'create_user.bat',
    'generate_test_image.bat'
]

for file in test_files:
    path = os.path.join(test_dir, file)
    if os.path.exists(path):
        size = os.path.getsize(path)
        if size > 1024*1024:
            size_str = f"{size / (1024*1024):.1f} MB"
        elif size > 1024:
            size_str = f"{size / 1024:.1f} KB"
        else:
            size_str = f"{size} B"
        print(f"  ✓ {file:<35} ({size_str})")
    else:
        print(f"  ○ {file:<35} (ready to create)")

print("\n" + "=" * 60)
