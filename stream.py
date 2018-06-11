import cv2
import io
import picamera
import logging
import socketserver
from http import server
import numpy as np
import os
import yaml
import requests
import json

server_url = 'http://0.0.0.0:8080'
cascadePath1 = "face_recognization/Cascades/haarcascade_frontalface_default.xml"
# cascadePath2 = "face_recognization/Cascades/haarcascade_profileface.xml"
namePath = "face_recognization/trainer/name.yml"
faceCascade1 = cv2.CascadeClassifier(cascadePath1)
# faceCascade2 = cv2.CascadeClassifier(cascadePath2)
recognizer1 = cv2.face.LBPHFaceRecognizer_create()
# recognizer2 = cv2.face.LBPHFaceRecognizer_create()
recognizer1.read('face_recognization/trainer/trainer100.yml')
# recognizer2.read('face_recognization/trainer/profiletrainer.yml')

font = cv2.FONT_HERSHEY_SIMPLEX

VALID_FACE = 1
NO_FACE = 0
INVALID_FACE = -1

def intersection(rect1, rect2):
    x = max(rect1[0], rect2[0])
    y = max(rect1[1], rect2[1])
    w = min(rect1[0] + rect1[2], rect2[0] + rect2[2]) - x
    h = min(rect1[1] + rect1[3], rect2[1] + rect2[3]) - y

    if w <= 0 or h <= 0: return False
    return True

class Stream():
    def __init__(self):
        # open camera
        self.cam = cv2.VideoCapture(0)
        self.cam.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        self.cam.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
        self.cam.set(cv2.CAP_PROP_FPS, 24)

        # Define min window size to be recognized as a face
        self.minW = 0.1 * self.cam.get(cv2.CAP_PROP_FRAME_WIDTH)
        self.minH = 0.1 * self.cam.get(cv2.CAP_PROP_FRAME_HEIGHT)

        # load valid person's name
        with open(namePath, 'r') as stream:
            try:
                self.names = yaml.load(stream)
            except yaml.YAMLError as e:
                print(e)

    def release(self):
        self.cam.release()

    def get_frame(self):
        rval, image = self.cam.read()
        image = cv2.flip(image, -1) # Flip vertically
        ret, jpeg = cv2.imencode('.jpg', image)
        return jpeg.tostring()

    def recognize(self):
        status = NO_FACE
        rval, image = self.cam.read()
        image = cv2.flip(image, -1) # Flip vertically
        gray = cv2.cvtColor(image,cv2.COLOR_BGR2GRAY)

        faces = faceCascade1.detectMultiScale(
            gray,
            scaleFactor = 1.3,
            minNeighbors = 5
        )

        for (x, y, w, h) in faces:
            id, confidence = recognizer1.predict(gray[y:y+h,x:x+w])

            # Check if confidence is less them 100 ==> "0" is perfect match
            if (confidence <= 100):
                nameId = self.names[id]
                status = VALID_FACE
                cv2.rectangle(image, (x, y), (x + w, y + h), (255,0,0), 2)
            else:
                nameId = "unknown"
                status = INVALID_FACE
                cv2.rectangle(image, (x, y), (x + w, y + h), (0,0,255), 2)

            cv2.putText(image, str(nameId), (x + 5, y - 5), font, 1, (255,255,255), 2)
            cv2.putText(image, str(confidence), (x + 5, y + h-5), font, 1, (255,255,0), 1)

        ret, jpeg = cv2.imencode('.jpg', image)
        return status, jpeg.tostring()

class StreamingHandler(server.BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/':
            self.send_response(200)
            self.send_header('Age', 0)
            self.send_header('Cache-Control', 'no-cache, private')
            self.send_header('Pragma', 'no-cache')
            self.send_header('Content-Type', 'multipart/x-mixed-replace; boundary=FRAME')
            self.end_headers()
            try:
                while True:
                    result, frame = output.recognize()

                    self.wfile.write(b'--FRAME\r\n')
                    self.send_header('Content-Type', 'image/jpeg')
                    self.send_header('Content-Length', len(frame))
                    self.end_headers()
                    self.wfile.write(frame)
                    self.wfile.write(b'\r\n')

                    # send recognization result to server
                    requests.post(server_url + '/face_recognize', json = {"result": result})

            except Exception as e:
                logging.warning(
                    'Removed streaming client %s: %s',
                    self.client_address, str(e))
        else:
            self.send_error(404)
            self.end_headers()

class StreamingServer(socketserver.ThreadingMixIn, server.HTTPServer):
    allow_reuse_address = True
    daemon_threads = True

if __name__ == '__main__':
    print("[STREAM INFO] prepare camera")
    output = Stream()
    print("[STREAM INFO] start streaming")
    try:
        address = ('', 8160)
        server = StreamingServer(address, StreamingHandler)
        server.serve_forever()
    except KeyboardInterrupt as e:
        output.release()
