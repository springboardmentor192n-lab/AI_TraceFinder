from PIL import Image
import os
import cv2
import numpy as np

output_dir = r'd:\Infosys-INTERNSHIP\AI_TraceFinder_Complete\pdf_pages'

print("="*80)
print("PDF INTERFACE ANALYSIS")
print("="*80)

pages_analysis = []

for i in range(1, 16):
    img_path = os.path.join(output_dir, f'page_{i}.png')
    if os.path.exists(img_path):
        try:
            # Load image
            img_pil = Image.open(img_path)
            img_cv = cv2.imread(img_path)
            
            if img_cv is None:
                print(f"Page {i}: Could not load image")
                continue
            
            width, height = img_pil.size
            
            # Convert to grayscale
            gray = cv2.cvtColor(img_cv, cv2.COLOR_BGR2GRAY)
            
            # Detect edges
            edges = cv2.Canny(gray, 50, 150)
            edge_count = np.sum(edges > 0)
            
            # Detect contours (potential UI elements)
            contours, _ = cv2.findContours(edges, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
            large_contours = [c for c in contours if cv2.contourArea(c) > 100]
            
            # Detect colors (for visualizations and UI elements)
            # Convert BGR to HSV
            hsv = cv2.cvtColor(img_cv, cv2.COLOR_BGR2HSV)
            
            # Count distinct hues and saturation levels
            unique_colors = len(np.unique(gray))
            
            # Estimate text vs non-text areas
            _, text_thresh = cv2.threshold(gray, 200, 255, cv2.THRESH_BINARY_INV)
            text_area = np.sum(text_thresh > 0)
            text_percentage = (text_area / (width * height)) * 100
            
            analysis = {
                'page': i,
                'resolution': f'{width}x{height}',
                'edge_count': edge_count,
                'detected_elements': len(large_contours),
                'unique_colors': unique_colors,
                'estimated_text_area': f'{text_percentage:.1f}%'
            }
            pages_analysis.append(analysis)
            
            print(f"\nPage {i}:")
            print(f"  Resolution: {width}x{height}")
            print(f"  Edge features detected: {edge_count}")
            print(f"  UI elements detected: {len(large_contours)}")
            print(f"  Unique colors: {unique_colors}")
            print(f"  Estimated text area: {text_percentage:.1f}%")
            
        except Exception as e:
            print(f"Error analyzing page {i}: {e}")

print("\n" + "="*80)
print(f"SUMMARY: Analyzed {len(pages_analysis)} pages")
print("="*80)
