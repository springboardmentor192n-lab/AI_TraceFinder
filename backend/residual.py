import cv2

def extract(image):

    blur = cv2.GaussianBlur(image,(5,5),0)

    residual = image - blur

    return residual