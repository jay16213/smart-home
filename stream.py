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

server_url = 'http://192.168.137.172:8080'
cascadePath1 = "face_recognization/Cascades/lbpcascade_frontalface_improved.xml"
cascadePath2 = "face_recognization/Cascades/haarcascade_profileface.xml"
namePath = "face_recognization/trainer/name.yml"
faceCascade1 = cv2.CascadeClassifier(cascadePath1)
faceCascade2 = cv2.CascadeClassifier(cascadePath2)
recognizer1 = cv2.face.LBPHFaceRecognizer_create()
recognizer2 = cv2.face.LBPHFaceRecognizer_create()
recognizer1.read('face_recognization/trainer/fronttrainer.yml')
recognizer2.read('face_recognization/trainer/profiletrainer.yml')

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
        self.cam.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
        self.cam.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
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

        statusFront, (x1, y1, w1, h1), nameIdFront, confidenceFront = self._recognizeFront(image, gray)
        if(statusFront != NO_FACE):
            if(statusFront == INVALID_FACE):
                cv2.rectangle(image, (x1, y1), (x1 + w1, y1 + h1), (0,0,255), 2)
            else:
                cv2.rectangle(image, (x1, y1), (x1 + w1, y1 + h1), (255,0,0), 2)
            cv2.putText(image, str(nameIdFront), (x1 + 5,y1 - 5), font, 1, (255,255,255), 2)
            cv2.putText(image, str(confidenceFront), (x1 + 5,y1 + h1-5), font, 1, (255,255,0), 1)

        statusProfile, (x2, y2, w2, h2), nameIdProfile, confidenceProfile = self._recognizeProfile(image, gray)
        if(statusProfile != NO_FACE):
            if(statusProfile == INVALID_FACE):
                cv2.rectangle(image, (x2, y2), (x2 + w2, y2 + h2), (0,0,255), 2)
            else:
                cv2.rectangle(image, (x2, y2), (x2 + w2, y2 + h2), (0,255,0), 2)
            cv2.putText(image, str(nameIdProfile), (x2 + 5,y2 - 5), font, 1, (255,255,255), 2)
            cv2.putText(image, str(confidenceProfile), (x2 + 5,y2 + h2 - 5), font, 1, (255,255,0), 1)

        ret, jpeg = cv2.imencode('.jpg', image)
        if(statusFront == INVALID_FACE or statusProfile == INVALID_FACE):
            if(not intersection((x1, y1, w1, h1), (x2, y2, w2, h2))):
                status = INVALID_FACE
        elif(statusFront == NO_FACE and statusProfile == NO_FACE):
            status = NO_FACE
        else:
            status = VALID_FACE

        return status, jpeg.tostring()

    def _recognizeFront(self, image, gray):
        status = NO_FACE
        nameId = ""
        confidence = -1
        faces = faceCascade1.detectMultiScale(
            gray,
            scaleFactor = 1.2,
            minNeighbors = 5,
            minSize = (int(self.minW), int(self.minH)),
        )

        xx = yy = ww = hh = -1
        for (x, y, w, h) in faces:
            xx = x
            yy = y
            ww = w
            hh = h
            id, _confidence = recognizer1.predict(gray[y:y+h,x:x+w])
            confidence = _confidence
            # Check if confidence is less them 100 ==> "0" is perfect match
            if (confidence <= 75):
                nameId = self.names[id]
                status = VALID_FACE
                # confidence = "  {0}%".format(round(100 - confidence))
            else:
                nameId = "unknown"
                status = INVALID_FACE
                # confidence = "  {0}%".format(round(confidence))

        return status, (xx, yy, ww, hh), nameId, confidence

    def _recognizeProfile(self, image, gray):
        status = NO_FACE
        nameId = ""
        confidence = -1
        faces = faceCascade2.detectMultiScale(
            gray,
            scaleFactor = 1.2,
            minNeighbors = 5,
            minSize = (int(self.minW), int(self.minH)),
        )

        xx = yy = ww = hh = -1
        for (x, y, w, h) in faces:
            xx = x
            yy = y
            ww = w
            hh = h
            id, _confidence = recognizer2.predict(gray[y:y+h,x:x+w])
            confidence = _confidence
            # Check if confidence is less them 100 ==> "0" is perfect match
            if (confidence <= 75):
                nameId = self.names[id]
                status = VALID_FACE
                # confidence = "  {0}%".format(round(100 - confidence))
            else:
                nameId = "unknown"
                status = INVALID_FACE
                # confidence = "  {0}%".format(round(confidence))

        return status, (xx, yy, ww, hh), nameId, confidence

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
    output = Stream()
    try:
        address = ('', 8160)
        server = StreamingServer(address, StreamingHandler)
        server.serve_forever()
    except KeyboardInterrupt as e:
        output.release()
