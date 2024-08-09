# Speed Estimator Documentation

## Table of Contents

1. [Introduction](#1-introduction)
2. [Monograph Information](#2-monograph-information)
3. [System Architecture](#3-system-architecture)
4. [Installation](#4-installation)
   1. [Dependencies](#41-dependencies)
   2. [Setting up Environment](#42-setting-up-environment)
5. [Configuration](#5-configuration)
   1. [Settings File](#51-settings-file)
   2. [Environment Variables](#52-environment-variables)
6. [Running Speed Estimator](#6-running-speedestimator)
7. [License](#7-license)

## 1. Introduction

Welcome to the documentation for the "Speed Estimator" project. This system is designed for vehicle speed estimation using machine learning models, primarily targeting embedded systems. It includes functionalities such as vehicle detection, tracking, speed estimation, and video creation with speed annotations.

## 2. Monograph Information

This project was developed as part of a **Monograph** for the completion of a degree. The full monograph document, which details the research, methodology, and findings, is available in the repository under the `monograph/` folder.

You can find the thesis document [here](monograph/TCC-MarceloBarreto.pdf).

## 3. System Architecture

The project follows a modular architecture with the main components being the Speed Estimator, utility functions, and a configuration file. The models used for vehicle detection and speed estimation are optimized for CPU to support low-cost embedded systems.

## 4. Installation

To install and set up the Speed Estimator on your machine, follow the steps below.

### 4.1 Dependencies

Ensure you have [Miniconda](https://docs.anaconda.com/free/miniconda/index.html) installed on your system. This project requires Python version 3.10.13.

### 4.2 Setting up Environment

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

## 5. Configuration

The Speed Estimator can be configured using the `settings.ini` file and environment variables.

### 5.1 Settings File

The `settings.ini` file contains configuration options for various components.

  ```ini
    [settings]
    SE_MODEL_PATH=./models_detection/best_speed_estimator.pt
    VD_MODEL_PATH=./models_detection/yolov8n_openvino_model
    SPEED_LIMIT=30
    MAX_CBBA=1871924.75
  ```
### 5.2 Environment Variables

Create a `.env` file by copying the `.env.example` file. This file is necessary for sending email notifications when a vehicle exceeds the speed limit.

  ```bash
    SENDER=
    PASSWORD=
    RECEIVER=
  ```

## 6. Running Speed Estimator

To run the Speed Estimator on a specific video:
  ```bash
    python3 main.py ./sample_video.mp4
  ```
An example can be downloaded at [example.mp4](https://drive.google.com/file/d/1q5DmC_oy8UEB_vuZH2aX4GOLp29wHAE-/view?usp=sharing)

## 7 LICENSE

This project is licensed under the [MIT License](LICENSE).

