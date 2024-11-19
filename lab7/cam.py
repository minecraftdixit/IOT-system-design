import dlib
import cv2
from picamera2 import Picamera2, Preview
import time
picam2 = Picamera2()
camera_config = picam2.create_preview_configuration()
picam2.configure(camera_config)
picam2.start_preview(Preview.QTGL)
picam2.start()
picam2.capture_file("test.jpg")
img = dlib.load_rgb_image('test.jpg')

detector = dlib.get_frontal_face_detector()
bboxes = detector(img, 1)

for b in bboxes:
    cv2.rectangle(img, (b.left(), b.top()), (b.right(), b.bottom()), (0, 255, 0), 2)

dlib.save_image(img, 'result.jpg')
