@echo off
title Generate Test Image
cd C:\Users\tejap\Downloads\Trace_finder-20260402T041728Z-1-001\Trace_finder
echo Generating test image...
echo.
python generate_test_image.py
echo.
echo Test image created! You can now upload it in TraceFinder.
pause

# Load and compare images from different scanners
from dataset_exploration import ImageAnalyzer

analyzer = ImageAnalyzer()
analyzer.compare_scanners('dataset_path')

# Extract fingerprints
from dataset_exploration import ResidualExtractor

residual = ResidualExtractor.extract_laplacian_residual(image)
