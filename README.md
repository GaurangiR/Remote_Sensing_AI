Remote Sensing AI Using Minimal Input
Abstract
This project focuses on reconstructing high-resolution satellite images from corrupted or abstract inputs using deep learning techniques. Inspired by DARPA's vision of geospatial interpretation from minimal data, the objective is to develop a deep neural architecture capable of generating near-original satellite imagery from inputs with degraded visual fidelity (e.g., blurred, masked, or noisy images). The approach leverages autoencoders combined with structural and perceptual loss functions to learn semantically meaningful representations for reconstruction.

Table of Contents
Project Motivation

Problem Statement

Architecture

Dataset Description

Methodology

Training Details


Project Motivation
In numerous real-world scenarios—such as natural disasters, low-bandwidth image transmission, or partial satellite coverage—geospatial data may be available only in a corrupted or highly abstract form. The ability to reconstruct usable satellite imagery from such limited inputs has implications across disaster management, environmental monitoring, and national security.

This project aims to address this challenge by training a model that can perform meaningful reconstruction of corrupted satellite images, thereby acting as a visual inference system that "fills in" missing or degraded information.

Problem Statement
Given a corrupted satellite image input (blurred, masked, or noisy), the objective is to accurately reconstruct the original uncorrupted image. The reconstruction quality is evaluated using both pixel-wise and perceptual similarity metrics.

Architecture
The core model is a convolutional autoencoder with skip connections to preserve spatial information during encoding and decoding. The network is trained using a composite loss function incorporating:

Mean Squared Error (MSE): Penalizes pixel-wise differences

Structural Similarity Index Measure (SSIM): Captures structural fidelity

Perceptual Loss: Utilizes intermediate feature maps from a pre-trained VGG16 network to encourage high-level semantic accuracy

plaintext
Copy
Edit
Input Corrupted Image
        │
     Encoder
        ↓
 Latent Representation
        ↓
     Decoder
        ↓
Reconstructed Image
        ↓
  Loss Functions (MSE + SSIM + VGG)
Dataset Description
UCMerced LandUse Dataset

Source: University of California, Merced

Classes: 21 land-use types (e.g., residential, freeway, forest, airplane, baseball diamond)

Image Size: 256x256 pixels, RGB

Total Images: 2,100 (100 per class)

Preprocessing: All images are resized and normalized

Input Corruption Techniques Applied:

Gaussian blur (simulates low-resolution imaging)

Random masking (simulates occlusion or partial view)

Gaussian noise (simulates poor signal-to-noise conditions)

Methodology
Data Corruption: Apply stochastic corruption techniques to simulate degraded satellite inputs.

Model Training: Use the corrupted image as input and the original as ground truth.

Loss Composition:

MSE ensures low-level pixel reconstruction

SSIM enforces structural accuracy

VGG-based perceptual loss drives semantic coherence

Validation: Evaluate model performance using held-out validation set and quantitative metrics.

Visualization: Compare inputs, ground truths, and outputs side by side.

Training Details
Environment: Google Colab with GPU acceleration

Framework: TensorFlow 2.x and Keras

Batch Size: 32

Epochs: 50

Optimizer: Adam (learning rate: 1e-4)

Callbacks: Early stopping and model checkpointing for best performance retention

