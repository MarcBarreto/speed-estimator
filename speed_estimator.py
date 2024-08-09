import os
import cv2
import utils_detection
import torch
import timeit
import numpy as np
import supervision as sv
from datetime import datetime
from utils_detection import create_file
from ultralytics import YOLO

class SpeedEstimator():
    def __init__(self, config):
        self.max_cbba = config('MAX_CBBA', cast=float)
        self.speed_limit = config('SPEED_LIMIT', cast=int)
        self.model = torch.jit.load(config('SE_MODEL_PATH'))

        os.environ['KMP_DUPLICATE_LIB_OK'] = 'TRUE'

        now = datetime.now()
        today = now.strftime('%Y_%m_%d')
        time = now.strftime('%Hh_%Mm_%Ss')
        utils_detection.create_dir('./logs')
        if utils_detection.create_dir('./footages'):
            self.folder = f'./footages/day_{today}'
            self.file = f'speed_{time}.csv'
            create_file(self.folder, self.file)

        self.vd_model = YOLO(config('VD_MODEL_PATH'), task = 'detect')

        self.tracker = sv.ByteTrack()

        self.sender = config('SENDER')
        self.password = config('PASSWORD')
        self.receiver = config('RECEIVER')

        self.file = os.path.join(self.folder, self.file)

        self.frames = []
        self.cbba_file = {}

    def predict(self, data : list):
        device = 'cuda' if torch.cuda.is_available() else 'cpu'
        data = torch.tensor([data], device = device)
        data = data.unsqueeze(dim = 0)
        self.model.to(device)
        self.model.eval()
        target = torch.round(self.model(data)).cpu().detach().numpy()
        return target

    def tracking(self, image: bytearray, frame_idx : int):
        classes = [2, 3, 5, 7] 
        
        box_annotator = sv.BoundingBoxAnnotator()
        label_annotator = sv.LabelAnnotator()

        result = self.vd_model(image)[0]
        
        detections = sv.Detections.from_ultralytics(result)
        detections = self.tracker.update_with_detections(detections)

        self.frames.append(image)
        
        if result and result[0].boxes.id is not None:
            detections.tracker_id = result[0].boxes.id.cpu().numpy().astype(int)

        detections = detections[np.isin(detections.class_id, classes)]
        labels = []
        if detections.tracker_id is not None:
            for idx in range(len(detections.tracker_id)):
                tracker_id = detections.tracker_id[idx]
                class_name = result.names[detections.class_id[idx]]

                if tracker_id in self.cbba_file.keys():
                    self.cbba_file[tracker_id].append((frame_idx, utils_detection.calc_area(detections.xyxy[idx]), detections.xyxy[idx]))
                else:
                    self.cbba_file[tracker_id] = [(frame_idx, utils_detection.calc_area(detections.xyxy[idx]), detections.xyxy[idx])]
                labels.append(f'#{tracker_id} {class_name}')
            
            image = box_annotator.annotate(scene = image, detections = detections)
            image = label_annotator.annotate(scene = image, detections = detections, labels = labels)
                
        for key in list(self.cbba_file.keys()):
            if detections.tracker_id is None or key not in detections.tracker_id:
                if frame_idx - self.cbba_file[key][-1][0] >= 10:
                    try:
                        areas = utils_detection.linear_interpolation(self.cbba_file[key])
                        if len(areas) >= 60:
                            value = [(y / self.max_cbba) for (x, y, z) in areas]
                            speed = self.predict(value)
                            vehicle_key = key
                                
                            path = os.path.join(self.folder, f'vehicle_{vehicle_key}.mp4')
                            utils_detection.create_video(self.frames[areas[0][0]:areas[-1][0] + 1], path, self.fourcc, self.fps, self.width, self.height)
                            utils_detection.send_mail(path, speed, vehicle_key, self.sender, self.password, self.receiver)
                    
                            with open(self.file, 'a+') as f:
                                f.write(str(vehicle_key) + ';' + f'{speed:.2f}' + "\n")
                    except Exception as e:
                        utils_detection.write_log(f'Erro ao estimar velocidade do veiculo {vehicle_key}: {e}')
                    self.cbba_file.pop(key)

            frame_idx += 1
        #cv2.imshow('speed_estimator', image)

    def interface_speed_estimator_test(
        self,
        dir_videos,
    ):
        """
        Args:
            dir_videos (str): Directory path containing video files for testing.

        Description:
            This method performs testing on a set of video files in the specified directory. It reads each
            video, performs vehicle tracking using the ByteTrack(), and estimate the speed of detected objects.

        Input:
            Video frames from the video files in the specified directory.

        Output:
            None.
        """
        # Get absolute paths of video files in the specified directory
        cap = cv2.VideoCapture(dir_videos)
        ret = True

        self.fps = cap.get(cv2.CAP_PROP_FPS)
        self.width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        self.height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        self.fourcc = cv2.VideoWriter.fourcc(*'mp4v')
        time = datetime.now().strftime('%H_%M_%S')
        video_writer = cv2.VideoWriter(os.path.join(self.folder, f'gravacao_{time}.mp4'), fourcc = self.fourcc, fps = self.fps, frameSize = (self.width, self.height))
        frame_idx = 0

        while ret:
            # Read video frame
            ret, image = cap.read()
            if ret and image is not None:
                self.tracking(image, frame_idx)

                frame_idx += 1
                video_writer.write(image)

        cap.release()
        video_writer.release()
        
        # Print completion message
        print('Test completed')