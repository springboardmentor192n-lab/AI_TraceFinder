from PIL import Image, ImageDraw, ImageFont
import random

print("Creating test image...")

# Create a simple test document image
width, height = 800, 600
background_color = (240, 240, 240)  # Light gray
image = Image.new('RGB', (width, height), background_color)
draw = ImageDraw.Draw(image)

# Draw some document-like content
# White background area (like scanned document)
draw.rectangle([(50, 50), (750, 550)], fill=(255, 255, 255), outline=(0, 0, 0), width=2)

# Add some text-like patterns
text_y = 100
for i in range(15):
    # Random horizontal lines to simulate text
    line_height = random.randint(15, 25)
    start_x = random.randint(60, 80)
    end_x = random.randint(700, 740)
    draw.line([(start_x, text_y), (end_x, text_y)], fill=(50, 50, 50), width=2)
    text_y += line_height + 10

# Add some noise to simulate scanner artifacts
for _ in range(100):
    x = random.randint(50, 750)
    y = random.randint(50, 550)
    size = random.randint(1, 3)
    color = random.choice([(200, 200, 200), (180, 180, 180), (220, 220, 220)])
    draw.rectangle([(x, y), (x+size, y+size)], fill=color)

# Add a watermark-like pattern
draw.rectangle([(50, 50), (200, 150)], outline=(100, 100, 255), width=2)
draw.text((60, 60), "TEST", fill=(100, 100, 255))

# Save the image
image.save('test_document.jpg', 'JPEG', quality=85)
print("✅ Created: test_document.jpg")
print("   Size: 800x600 pixels")
print("   Type: JPEG document scan simulation")
print("\nYou can now upload this image in the TraceFinder UI!")
