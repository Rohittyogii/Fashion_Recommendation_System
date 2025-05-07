import os
import cv2
import numpy as np
import pandas as pd
from utils.preprocessing import preprocess_image
from utils.features import extract_features

IMAGE_DIR = 'images/image'

def get_all_image_paths(base_dir):
    image_paths = []
    for root, _, files in os.walk(base_dir):
        for file in files:
            if file.lower().endswith(('.jpg', '.jpeg', '.png')):
                full_path = os.path.join(root, file)
                relative_path = os.path.relpath(full_path, start='.')
                image_paths.append(relative_path)
    return image_paths

def main():
    image_paths = get_all_image_paths(IMAGE_DIR)
    records = []

    for img_path in image_paths:
        img = cv2.imread(img_path)
        if img is None:
            continue

        pre_img = preprocess_image(img)
        features = extract_features(pre_img)

        records.append({
            "image_path": img_path,
            "features": features.tolist()
        })

    df = pd.DataFrame(records)
    if not os.path.exists("models"):
        os.makedirs("models")
    df.to_pickle("models/image_features.pkl")

if __name__ == "__main__":
    main()
