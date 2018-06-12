import cv2
import io
import logging
import socketserver
from http import server
import numpy as np
import os
import requests

class Camera():
    def __init__(self):
        # open camera
        self.cam = cv2.VideoCapture(0)
        self.cam.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        self.cam.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
        self.cam.set(cv2.CAP_PROP_FPS, 25)

    def release(self):
        self.cam.release()

    def get_frame(self):
        rval, image = self.cam.read()
        image = cv2.flip(image, -1) # Flip vertically
        ret, jpeg = cv2.imencode('.jpg', image)
        return jpeg.tostring()

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
                    # global camera
                    frame = camera.get_frame()

                    self.wfile.write(b'--FRAME\r\n')
                    self.send_header('Content-Type', 'image/jpeg')
                    self.send_header('Content-Length', len(frame))
                    self.end_headers()
                    self.wfile.write(frame)
                    self.wfile.write(b'\r\n')

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
    camera = Camera()
    print("[STREAM INFO] start streaming")
    try:
        address = ('', 8161)
        server = StreamingServer(address, StreamingHandler)
        server.serve_forever()
    except KeyboardInterrupt as e:
        camera.release()
