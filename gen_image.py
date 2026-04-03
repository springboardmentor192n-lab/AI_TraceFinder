from PIL import Image
ImageSize = (800, 600)
img = Image.new('RGB', (800, 600), (240, 240, 240))
img.save('test_document.jpg', 'JPEG')
print('Test image created: test_document.jpg')
