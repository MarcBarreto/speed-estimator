# Speed Estimator Documentation

## Table of Contents

1. [Introduction](#1-introduction)
2. [System Architecture](#2-system-architecture)
3. [Installation](#3-installation)
   1. [Dependencies](#31-dependencies)
   2. [Setting up Environment](#32-setting-up-environment)
4. [Configuration](#4-configuration)
   1. [Settings File](#41-settings-file)
   2. [Environment Variables](#42-environment-variables)
5. [Running Speed Estimator](#5-running-speedestimator)
6. [License](#6-license)

## 1. Introduction

Welcome to the documentation for the "Speed Estimator" project. This system is designed for vehicle speed estimation using machine learning models, primarily targeting embedded systems. It includes functionalities such as vehicle detection, tracking, speed estimation, and video creation with speed annotations.

## 2. System Architecture

The project follows a modular architecture with the main components being the Speed Estimator, utility functions, and a configuration file. The models used for vehicle detection and speed estimation are optimized for CPU to support low-cost embedded systems.

## 3. Installation

To install and set up the Speed Estimator on your machine, follow the steps below.

### 3.1 Dependencies

Ensure you have [Miniconda](https://docs.anaconda.com/free/miniconda/index.html) installed on your system. This project requires Python version 3.10.13.

### 3.2 Setting up Environment

1. **Clone the Repository**:

   ```bash
   git clone https://github.com/yourusername/speed-estimator.git
   cd speed-estimator
   
2. **Create a Conda Environment**:

  ```bash
    conda create --name speed_estimator python=3.10.13
    conda activate speed_estimator
  ```

3. **Install Required Packages**:

  ```bash
    pip install -r requirements.txt
  ```

## 4. Configuration

The Speed Estimator can be configured using the `settings.ini` file and environment variables.

### 4.1 Settings File

The `settings.ini` file contains configuration options for various components.

  ```ini
    [settings]
    SE_MODEL_PATH=./models_detection/best_speed_estimator.pt
    VD_MODEL_PATH=./models_detection/yolov8n_openvino_model
    SPEED_LIMIT=30
    MAX_CBBA=1871924.75
  ```
### 4.2 Environment Variables

Create a `.env` file by copying the `.env.example` file. This file is necessary for sending email notifications when a vehicle exceeds the speed limit.

  ```bash
    SENDER=
    PASSWORD=
    RECEIVER=
  ```

## 5. Running Speed Estimator

To run the Speed Estimator on a specific video:
  ```bash
    python3 main.py ./videos/sample_video.mp4
  ```
An example can be downloaded at [example.mp4](https://drive.google.com/file/d/1q5DmC_oy8UEB_vuZH2aX4GOLp29wHAE-/view?usp=sharing)

## 6 LICENSE

This project is licensed under the [MIT License](LICENSE).

