# -*- coding: utf-8 -*-
"""Remote_Sensing_AI_Stargate.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1AU46Lbo4xkGIAQn-s47X_hBrObEEEg-t
"""

# Run this in Colab cell
!pip install matplotlib opencv-python numpy scikit-image

import os
import cv2
import numpy as np
import matplotlib.pyplot as plt
from skimage.util import random_noise
from google.colab import drive

from google.colab import drive
drive.mount('/content/drive')

import os

# Explore your drive
os.listdir("/content/drive/MyDrive")

dataset_path = "/content/drive/MyDrive/UCMerced_LandUse/Images" # Corrected the directory name to UCMerced_LandUse
classes = os.listdir(dataset_path) # Assign the list of subdirectories (classes) to the variable 'classes'
print(f"Found {len(classes)} classes:")
print(classes)

import cv2
import matplotlib.pyplot as plt

# Pick a class and list its images
sample_class = 'agricultural'
sample_class_path = os.path.join(dataset_path, sample_class)
images = os.listdir(sample_class_path)

# Display first 5 images
plt.figure(figsize=(15, 5))
for i in range(5):
    img_path = os.path.join(sample_class_path, images[i])
    img = cv2.imread(img_path)
    img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    plt.subplot(1, 5, i + 1)
    plt.imshow(img_rgb)
    plt.title(f"{sample_class} #{i+1}")
    plt.axis("off")
plt.tight_layout()
plt.show()

import numpy as np

# Use first image of 'agricultural' class
img_path = os.path.join(dataset_path, 'agricultural', images[0])
img = cv2.imread(img_path)

# Create folders
os.makedirs("processed/original", exist_ok=True)
os.makedirs("processed/blurred", exist_ok=True)
os.makedirs("processed/masked", exist_ok=True)
os.makedirs("processed/noisy", exist_ok=True)

# Save original
cv2.imwrite("processed/original/0.jpg", img)

# Blurred version
blurred = cv2.GaussianBlur(img, (15, 15), 0)
cv2.imwrite("processed/blurred/0.jpg", blurred)

# Masked version (black box)
masked = img.copy()
masked[50:150, 50:150] = 0
cv2.imwrite("processed/masked/0.jpg", masked)

# Noisy version
noise = np.random.randint(0, 50, img.shape, dtype='uint8')
noisy = cv2.add(img, noise)
cv2.imwrite("processed/noisy/0.jpg", noisy)

fig, axs = plt.subplots(1, 4, figsize=(16, 4))

titles = ["Original", "Blurred", "Masked", "Noisy"]
paths = [
    "processed/original/0.jpg",
    "processed/blurred/0.jpg",
    "processed/masked/0.jpg",
    "processed/noisy/0.jpg"
]

for i, path in enumerate(paths):
    img = cv2.imread(path)
    if img is not None:
        axs[i].imshow(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
        axs[i].set_title(titles[i])
        axs[i].axis("off")
    else:
        axs[i].set_title(f"Error: {titles[i]}")
        axs[i].axis("off")

plt.tight_layout()
plt.show()

import cv2
import numpy as np
import os
from tqdm import tqdm

def load_images(folder):
    images = []
    for filename in sorted(os.listdir(folder)):  # ensures consistent order
        img_path = os.path.join(folder, filename)
        img = cv2.imread(img_path)
        if img is not None:
            img = cv2.resize(img, (128, 128))  # standardize size
            img = img / 255.0  # normalize
            images.append(img)
    return np.array(images)

# Paths to folders (should already contain your processed images)
input_folders = ["processed/blurred", "processed/masked", "processed/noisy"]
target_folder = "processed/original"

# Load targets (ground truth originals)
y = load_images(target_folder)

# Load inputs (corrupted)
X = []
for folder in input_folders:
    imgs = load_images(folder)
    X.extend(imgs)

# Repeat y accordingly (since we use each original for all 3 corruptions)
y = np.tile(y, (len(input_folders), 1, 1, 1))

X = np.array(X)
print(f"Input shape: {X.shape}, Target shape: {y.shape}")

import tensorflow as tf
from tensorflow.keras import layers, models

def build_autoencoder(input_shape=(128, 128, 3)):
    input_img = layers.Input(shape=input_shape)

    # Encoder
    x = layers.Conv2D(32, (3, 3), activation='relu', padding='same')(input_img)
    x = layers.MaxPooling2D((2, 2), padding='same')(x)
    x = layers.Conv2D(64, (3, 3), activation='relu', padding='same')(x)
    x = layers.MaxPooling2D((2, 2), padding='same')(x)

    # Bottleneck
    x = layers.Conv2D(128, (3, 3), activation='relu', padding='same')(x)

    # Decoder
    x = layers.UpSampling2D((2, 2))(x)
    x = layers.Conv2D(64, (3, 3), activation='relu', padding='same')(x)
    x = layers.UpSampling2D((2, 2))(x)
    decoded = layers.Conv2D(3, (3, 3), activation='sigmoid', padding='same')(x)

    autoencoder = models.Model(input_img, decoded)
    autoencoder.compile(optimizer='adam', loss='mse')

    return autoencoder

autoencoder = build_autoencoder()
autoencoder.summary()

history = autoencoder.fit(X, y, epochs=300, batch_size=32, shuffle=True, validation_split=0.1)

import matplotlib.pyplot as plt

def show_reconstruction(autoencoder, X, y, n=5):
    decoded_imgs = autoencoder.predict(X[:n])

    plt.figure(figsize=(15, 6))
    for i in range(n):
        # Input (corrupted)
        ax = plt.subplot(3, n, i + 1)
        plt.imshow(X[i])
        plt.title("Corrupted")
        plt.axis("off")

        # Output (reconstructed)
        ax = plt.subplot(3, n, i + 1 + n)
        plt.imshow(decoded_imgs[i])
        plt.title("Reconstructed")
        plt.axis("off")

        # Ground truth
        ax = plt.subplot(3, n, i + 1 + 2 * n)
        plt.imshow(y[i])
        plt.title("Original")
        plt.axis("off")
    plt.tight_layout()
    plt.show()

show_reconstruction(autoencoder, X, y)

# Re-run visualization to evaluate
show_reconstruction(autoencoder, X, y, n=5)

from sklearn.metrics import mean_squared_error

# Predict reconstructed images
reconstructed = autoencoder.predict(X)

# Reshape arrays for pixel-wise comparison
X_flat = y.reshape(len(y), -1)
reconstructed_flat = reconstructed.reshape(len(reconstructed), -1)

mse_scores = []
for i in range(len(y)):
    mse = mean_squared_error(X_flat[i], reconstructed_flat[i])
    mse_scores.append(mse)

avg_mse = np.mean(mse_scores)
print(f"Average MSE: {avg_mse}")

pip install scikit-image

from skimage.metrics import structural_similarity as ssim

def calculate_ssim(y_true, y_pred):
    ssim_scores = []
    for i in range(len(y_true)):
        score = ssim(y_true[i], y_pred[i], channel_axis=2, data_range=1.0)
        ssim_scores.append(score)
    return np.mean(ssim_scores)

# Call it again
avg_ssim = calculate_ssim(y, reconstructed)
print(f"Average SSIM: {avg_ssim:.4f}")

!pip install tensorflow-addons

import tensorflow as tf
import tensorflow.keras.backend as K

def combined_loss(y_true, y_pred):
    # MSE Loss
    mse = K.mean(K.square(y_true - y_pred))

    # SSIM Loss
    ssim = tf.image.ssim(y_true, y_pred, max_val=1.0)
    ssim_loss = 1 - ssim  # because higher SSIM = better

    # Final Combined Loss
    return mse + tf.reduce_mean(ssim_loss)

autoencoder.compile(optimizer='adam', loss=combined_loss)

from skimage.metrics import structural_similarity as ssim
import numpy as np

def calculate_ssim(y_true, y_pred):
    ssim_scores = []
    for i in range(len(y_true)):
        score = ssim(y_true[i], y_pred[i], channel_axis=-1, data_range=1.0)
        ssim_scores.append(score)
    return np.mean(ssim_scores)

# Get predictions again
reconstructed = autoencoder.predict(X)

# Calculate SSIM
avg_ssim = calculate_ssim(y, reconstructed)
print(f"📊 Average SSIM after training: {avg_ssim:.4f}")

from tensorflow.keras.applications import VGG16
from tensorflow.keras.models import Model

# Pretrained VGG16 without top classification layers
vgg = VGG16(include_top=False, weights='imagenet', input_shape=(64, 64, 3))  # adjust shape if needed

# Freeze all layers
vgg.trainable = False

# Extract feature maps from an early layer (block1_conv2 is good)
feature_extractor = Model(inputs=vgg.input, outputs=vgg.get_layer('block1_conv2').output)

import tensorflow.keras.backend as K

def perceptual_loss(y_true, y_pred):
    # Resize to match VGG input (64x64x3)
    y_true_resized = tf.image.resize(y_true, (64, 64))
    y_pred_resized = tf.image.resize(y_pred, (64, 64))

    # Get VGG features
    true_features = feature_extractor(y_true_resized)
    pred_features = feature_extractor(y_pred_resized)

    # Calculate feature MSE
    feature_loss = K.mean(K.square(true_features - pred_features))

    # Pixel-level MSE
    pixel_loss = K.mean(K.square(y_true - y_pred))

    # Combine both
    return 0.5 * pixel_loss + 0.5 * feature_loss

import os
import cv2
import numpy as np
from tqdm import tqdm

base_path = '/content/drive/MyDrive/UCMerced_LandUse/Images'
classes = sorted(os.listdir(base_path))  # 21 classes

def load_and_corrupt_images(base_path, classes, n_images_per_class=25):
    clean_images = []
    corrupted_images = []

    for cls in classes:
        class_path = os.path.join(base_path, cls)
        images_in_class = os.listdir(class_path)[:n_images_per_class]  # first N images
        for img_name in images_in_class:
            img_path = os.path.join(class_path, img_name)
            img = cv2.imread(img_path)
            img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            img = cv2.resize(img, (128, 128))
            img = img.astype('float32') / 255.0

            clean_images.append(img)

            # Apply random corruption
            corrupted = img.copy()

            # Random corruption: blur, noise, and masking
            if np.random.rand() < 0.33:
                corrupted = cv2.GaussianBlur(corrupted, (5, 5), 0)
            if np.random.rand() < 0.33:
                noise = np.random.normal(0, 0.1, corrupted.shape)
                corrupted = np.clip(corrupted + noise, 0.0, 1.0)
            if np.random.rand() < 0.33:
                x, y = np.random.randint(30, 100), np.random.randint(30, 100)
                corrupted[y:y+20, x:x+20] = 0

            corrupted_images.append(corrupted)

    return np.array(clean_images), np.array(corrupted_images)

clean_images, corrupted_images = load_and_corrupt_images(base_path, classes, n_images_per_class=25)
print(clean_images.shape, corrupted_images.shape)  # (525, 128, 128, 3)

from tensorflow.keras.callbacks import EarlyStopping, ReduceLROnPlateau

callbacks = [
    EarlyStopping(monitor='val_loss', patience=20, restore_best_weights=True),
    ReduceLROnPlateau(monitor='val_loss', factor=0.5, patience=10, verbose=1)
]

autoencoder.fit(
    corrupted_images, clean_images,
    epochs=300,
    batch_size=16,
    validation_split=0.1,
    callbacks=callbacks
)

from skimage.metrics import structural_similarity as ssim
from skimage.metrics import peak_signal_noise_ratio as psnr
import numpy as np

reconstructed_images = autoencoder.predict(corrupted_images)

from skimage.metrics import structural_similarity as ssim
from skimage.metrics import peak_signal_noise_ratio as psnr

ssim_scores = []
psnr_scores = []

for i in range(len(clean_images)):
    original = clean_images[i]
    reconstructed = reconstructed_images[i]

    ssim_val = ssim(original, reconstructed, channel_axis=-1, win_size=7, data_range=1.0)
    psnr_val = psnr(original, reconstructed, data_range=1.0)

    ssim_scores.append(ssim_val)
    psnr_scores.append(psnr_val)

print(f"✅ Average SSIM: {np.mean(ssim_scores):.4f}")
print(f"✅ Average PSNR: {np.mean(psnr_scores):.2f} dB")

import matplotlib.pyplot as plt

i = np.random.randint(len(clean_images))
plt.figure(figsize=(12,4))

plt.subplot(1,3,1)
plt.title("Original")
plt.imshow(clean_images[i])
plt.axis('off')

plt.subplot(1,3,2)
plt.title("Corrupted")
plt.imshow(corrupted_images[i])
plt.axis('off')

plt.subplot(1,3,3)
plt.title("Reconstructed")
plt.imshow(reconstructed_images[i])
plt.axis('off')

plt.show()