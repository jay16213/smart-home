import cv2
import io
import logging
import socketserver
from http import server
import numpy as np
from urllib.request import urlopen
import requests
import face_recognition
from encoding import loadEncoding
from threading import Thread
from queue import Queue

font = cv2.FONT_HERSHEY_SIMPLEX
server_url = "http://0.0.0.0:8080"
PI_URL = "http://192.168.137.220:8161"

VALID_FACE = 1
NO_FACE = 0
INVALID_FACE = -1

raw_frame_queue = Queue()
finished_frame_queue = Queue()

class Stream():
    def __init__(self):
        print("[INFO] Capture stream resource")
        self.cap = cv2.VideoCapture(PI_URL)
        print("[INFO] Loading known face encodings")
        self.known_face_encodings, self.known_names = loadEncoding('v2')

        self._get_frame_thread = Thread(target=self.get_frame_in_thread)
        self._get_frame_thread.daemon = True
        self._recognize_thread = Thread(target=self.run_in_thread)
        self._recognize_thread.daemon = True

        print("[INFO] Finished initialization. Start streaming")
        self._get_frame_thread.start()
        self._recognize_thread.start()

    def release(self):
        self.cap.release()
        self._get_frame_thread.join()
        self._recognize_thread.join()

    def run_in_thread(self):
        while True:
            frame = raw_frame_queue.get()
            if frame is None:
                break
            status, frame = self.recognize_in_thread(frame)
            # send recognization result to server
            requests.post(server_url + '/face_recognize', json = {"result": status})

            # if there are too many finished frames, clear all of them
            if finished_frame_queue.qsize() > 10:
                finished_frame_queue.queue.clear()

            finished_frame_queue.put(frame)
            raw_frame_queue.task_done()

    def get_frame_in_thread(self):
        while True:
            # if there are too many unprocessed frames, clear all of them
            if raw_frame_queue.qsize() > 10:
                raw_frame_queue.queue.clear()

            res, frame = self.cap.read()
            raw_frame_queue.put(frame)

    def recognize_in_thread(self, frame):
        status = NO_FACE
        small_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)

        # Find all the faces and face encodings in the current frame of video
        face_locations = face_recognition.face_locations(small_frame)
        face_encodings = face_recognition.face_encodings(small_frame, face_locations)

        for (top, right, bottom, left), face_encoding in zip(face_locations, face_encodings):
            top *= 4
            right *= 4
            bottom *= 4
            left *= 4

            # See if the face is a match for the known face(s)
            matches = face_recognition.compare_faces(self.known_face_encodings, face_encoding, tolerance=0.5)

            # If a match was found in known_face_encodings, just use the first one.
            if True in matches:
                status = VALID_FACE
                first_match_index = matches.index(True)
                cv2.rectangle(frame, (left, top), (right, bottom), (0, 255, 0), 2)
                cv2.putText(frame, self.known_names[first_match_index], (left + 6, bottom - 6), font, 1.0, (255, 255, 255), 1)
            else:
                if status != VALID_FACE:
                    status = INVALID_FACE
                cv2.rectangle(frame, (left, top), (right, bottom), (0, 0, 255), 2)
                cv2.putText(frame, 'Unknown', (left + 6, bottom - 6), font, 1.0, (255, 255, 255), 1)

        if status == INVALID_FACE:
            cv2.imwrite('v2/stranger/stranger.jpg', frame)

        ret, jpeg = cv2.imencode('.jpg', frame)
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
                    frame = finished_frame_queue.get()

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
    stream = Stream()
    try:
        address = ('', 8160)
        server = StreamingServer(address, StreamingHandler)
        server.serve_forever()
    except KeyboardInterrupt as e:
        stream.release()
