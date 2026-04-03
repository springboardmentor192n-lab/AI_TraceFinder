import pickle
import numpy as np
import os

art_dir = r'C:\Users\tejap\Downloads\Trace_finder-20260402T041728Z-1-001\Trace_finder\artifacts'

# Load label encoder
le = pickle.load(open(os.path.join(art_dir, 'hybrid_label_encoder.pkl'), 'rb'))
print("Scanner classes available:")
print("=" * 50)
for i, scanner in enumerate(le.classes_):
    print(f"{i}: {scanner}")
print("=" * 50)
print(f"Total scanners: {len(le.classes_)}")

# Check for canon220
if 'canon220' in le.classes_:
    idx = np.where(le.classes_ == 'canon220')[0][0]
    print(f"\n✅ canon220 FOUND at index {idx}")
else:
    print(f"\n❌ canon220 NOT FOUND in label encoder")
    
# List similar scanner names
print("\nScanner names containing 'canon':")
for scanner in le.classes_:
    if 'canon' in scanner.lower():
        print(f"  - {scanner}")
