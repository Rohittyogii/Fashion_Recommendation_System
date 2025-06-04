from tensorflow.keras.applications.vgg16 import VGG16, preprocess_input
from tensorflow.keras.models import Model
import numpy as np

model = VGG16(weights="imagenet")
model = Model(inputs=model.input, outputs=model.get_layer("fc1").output)

def extract_features(img):
    img = np.expand_dims(img, axis=0)
    img = preprocess_input(img)
    features = model.predict(img)
    return features.flatten()
