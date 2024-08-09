from decouple import Config, RepositoryEnv
from collections import ChainMap

from speed_estimator import SpeedEstimator

import argparse

parser = argparse.ArgumentParser()
parser.add_argument("--rtsp_uri", type=str, default="")

opt = parser.parse_known_args()[0]

config = Config(ChainMap(RepositoryEnv("settings.ini"), RepositoryEnv(".env")))

estimator_obj = SpeedEstimator(config)

estimator_obj.interface_speed_estimator_test(
    dir_videos=opt.rtsp_uri,
)