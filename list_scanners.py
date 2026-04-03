import pickle
import os

art_dir = r'C:\Users\tejap\Downloads\Trace_finder-20260402T041728Z-1-001\Trace_finder\artifacts'

print("Checking label encoder...")
try:
    le = pickle.load(open(os.path.join(art_dir, 'hybrid_label_encoder.pkl'), 'rb'))
    print(f"\nAvailable scanners ({len(le.classes_)} total):")
    for scanner in sorted(le.classes_):
        print(f"  - {scanner}")
    
    if 'canon220' in le.classes_:
        print("\n✅ canon220 is AVAILABLE")
    else:
        print("\n❌ canon220 is NOT in the model")
        
except Exception as e:
    print(f"Error: {e}")
