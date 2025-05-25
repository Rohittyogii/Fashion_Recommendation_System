import cv2

def preprocess_image(img):
    img = cv2.resize(img, (224, 224))
    img = img / 255.0
    return img
