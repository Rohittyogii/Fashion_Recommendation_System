import os
import subprocess

# Step 1: Check if models/image_features.pkl exists
if not os.path.exists("models/image_features.pkl"):
    print("Building dataset...")
    subprocess.run(["python", "build_dataset.py"])
else:
    print("Dataset already built. Skipping build_dataset.py...")

# Step 2: Now launch Streamlit app
print("Starting Streamlit app...")
subprocess.run(["streamlit", "run", "app.py"])
