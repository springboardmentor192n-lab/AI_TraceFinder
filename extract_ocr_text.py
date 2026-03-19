import easyocr
import os
from PIL import Image
import json

output_dir = r'd:\Infosys-INTERNSHIP\AI_TraceFinder_Complete\pdf_pages'

# Initialize OCR reader for English
print("Initializing OCR reader...")
reader = easyocr.Reader(['en'], gpu=False)

print("="*80)
print("EXTRACTING TEXT FROM PDF PAGES USING OCR")
print("="*80)

all_text = {}
ocr_results = []

for i in range(1, 16):
    img_path = os.path.join(output_dir, f'page_{i}.png')
    if os.path.exists(img_path):
        print(f"\nProcessing Page {i}...")
        try:
            # Run OCR
            result = reader.readtext(img_path)
            
            # Extract text
            page_text = "\n".join([text[1] for text in result])
            all_text[f'page_{i}'] = page_text
            
            # Group by confidence
            high_conf = [text for text in result if text[2] > 0.5]
            med_conf = [text for text in result if 0.3 <= text[2] <= 0.5]
            low_conf = [text for text in result if text[2] < 0.3]
            
            print(f"  Found {len(result)} text elements")
            print(f"  High confidence: {len(high_conf)}")
            print(f"  Medium confidence: {len(med_conf)}")
            print(f"  Low confidence: {len(low_conf)}")
            
            # Print first few lines of text
            print(f"\n  Text preview:")
            for line in page_text.split('\n')[:10]:
                if line.strip():
                    print(f"    {line[:70]}")
            
            ocr_results.append({
                'page': i,
                'total_elements': len(result),
                'high_confidence': len(high_conf),
                'text_length': len(page_text)
            })
            
        except Exception as e:
            print(f"  Error processing page {i}: {e}")

# Save consolidated text
output_file = r'd:\Infosys-INTERNSHIP\AI_TraceFinder_Complete\pdf_text_extracted.txt'
with open(output_file, 'w', encoding='utf-8') as f:
    for page_num in sorted(all_text.keys()):
        f.write(f"\n{'='*80}\n")
        f.write(f"{page_num.upper()}\n")
        f.write(f"{'='*80}\n\n")
        f.write(all_text[page_num])

print("\n" + "="*80)
print(f"All text extracted and saved to: {output_file}")
print("="*80)

# Print summary
print("\nSUMMARY:")
for result in ocr_results:
    print(f"Page {result['page']}: {result['total_elements']} elements, {result['text_length']} chars")
