import torch
import torchvision.transforms as transforms
import torchvision.datasets as datasets
import timm
from ultralytics import YOLO
import time
import numpy as np
import matplotlib.pyplot as plt
from PIL import Image

# TODO: Make entire setup generalizable

# Load MNIST dataset
mnist_test = datasets.MNIST(root="./data", train=False, download=True)
images = [mnist_test[i][0] for i in range(10)]  # Take 10 images for testing

# Transform for EfficientNet (Preprocessing)
transform = transforms.Compose([
    transforms.Resize((224, 224)),  # EfficientNet expects 224x224
    transforms.Grayscale(num_output_channels=3),  # Convert grayscale to 3-channel RGB
    transforms.ToTensor(),
    transforms.Normalize([0.5], [0.5])
])

# Load EfficientNet B7 Model (timm)
efficientnet_model = timm.create_model("efficientnet_b7", pretrained=False)
efficientnet_model.eval()

# Load YOLO Model 
yolo_model = YOLO("yolov8n.pt") 

# Function to measure inference time and energy consumption (placeholder)
# TODO: update and move to benchmark.py to seperate models from benchmark logic
def measure_energy_consumption(model, preprocess, images, is_yolo=False):
    start_time = time.time()

    if is_yolo:
        results = [model(image) for image in images]
    else:
        with torch.no_grad():
            inputs = torch.stack([preprocess(image) for image in images])
            results = model(inputs)

    end_time = time.time()
    duration = end_time - start_time
    energy_consumed = np.random.uniform(0.5, 2.0)  # TODO: Only a placeholder for actual energy measurement
    return results, duration, energy_consumed

# Run inference on model A (EfficientNet)
eff_results, eff_time, eff_energy = measure_energy_consumption(efficientnet_model, transform, images)

# Run inference on model B (YOLO)
yolo_results, yolo_time, yolo_energy = measure_energy_consumption(yolo_model, None, images, is_yolo=True)

# Print results (not actual energy consumption)
print(f"EfficientNet B7 - Time: {eff_time:.3f}s, Energy: {eff_energy:.2f}J")
print(f"YOLO - Time: {yolo_time:.3f}s, Energy: {yolo_energy:.2f}J")
