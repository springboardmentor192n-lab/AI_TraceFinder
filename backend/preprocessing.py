import cv2
import numpy as np

def process(file):

    file_bytes = file.read()

    np_array = np.frombuffer(file_bytes, np.uint8)

    image = cv2.imdecode(np_array, cv2.IMREAD_COLOR)

    if image is None:
        raise Exception("Invalid image file. Please upload JPG or PNG.")

    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    resized = cv2.resize(gray, (512,512))

    return resized