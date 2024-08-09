from pathlib import Path
import torch
from ultralytics import YOLO
import sys
import os
import numpy as np

class Model:
    def __init__(
        self,
        config,
        stage,
        yolo_version,
    ):
        cuda = torch.cuda.is_available()
        self.yolo_version = yolo_version

        if stage == 'vehicle':
            path = Path(config('VEHICLE_PATH_MODEL_CPU', cast=str)) if not cuda else Path(config["VEHICLE_PATH_MODEL_GPU"])
        elif stage == 'plate':
            path = Path(config('LP_PATH_MODEL_CPU', cast=str)) if not cuda else Path(config["LP_PATH_MODEL_GPU"])
        elif stage == 'ocr':
            path = Path(config('CHARACTER_PATH_MODEL_CPU', cast=str)) if not cuda else Path(config["CHARACTER_PATH_MODEL_GPU"])

        if self.yolo_version == 'v5':
            self.model = torch.hub.load('ultralytics/yolov5', 'custom', path)
        elif self.yolo_version == 'v8':
            self.model = YOLO(path, task = 'detect')

    def detect(
        self,
        image: bytearray
    ):
        if self.yolo_version == 'v5':
            return self.model(image).xyxy[0].tolist()
        elif self.yolo_version == 'v8':
            return self.model(image)[0].boxes.data.tolist()