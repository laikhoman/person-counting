import os
import cv2
from .base_camera import BaseCamera

class Camera(BaseCamera):
    def __init__(self, channel):
        Camera.video_source = "rtsp://guest:pmb12345@10.0.0.106:554/Streaming/Channels/" + str(channel)

        if os.environ.get('OPENCV_CAMERA_SOURCE'):
            Camera.set_video_source(int(os.environ['OPENCV_CAMERA_SOURCE']))
        super(Camera, self).__init__()

    def __repr__(self):
        return Camera.video_source

    @staticmethod
    def set_video_source(source):
        Camera.video_source = source

    @staticmethod
    def frames():
        camera = cv2.VideoCapture(Camera.video_source)
        if not camera.isOpened():
            raise RuntimeError('Could not start camera.')

        while True:
            # read current frame
            _, img = camera.read()
            img = cv2.resize(img, (int(1280/2), int(720/2)))
            # encode as a jpeg image and return it
            yield cv2.imencode('.jpg', img)[1].tobytes()