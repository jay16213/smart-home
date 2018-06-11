# This is a demo of running face recognition on a Raspberry Pi.
# This program will print out the names of anyone it recognizes to the console.

# To run this, you need a Raspberry Pi 2 (or greater) with face_recognition and
# the picamera[array] module installed.
# You can follow this installation instructions to get your RPi set up:
# https://gist.github.com/ageitgey/1ac8dbe8572f3f533df6269dab35df65

import face_recognition
import picamera
import numpy as np
import cv2
from encoding import loadEncoding

font = cv2.FONT_HERSHEY_DUPLEX

camera = cv2.VideoCapture(0)
camera.set(cv2.CAP_PROP_FRAME_WIDTH, 320)
camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 240)
camera.set(cv2.CAP_PROP_FPS, 24)
output = np.empty((240, 320, 3), dtype=np.uint8)

# Load a sample picture and learn how to recognize it.
print("Loading known face image(s)")
known_face_encodings, known_names = loadEncoding()
# obama_image = face_recognition.load_image_file("jay.jpg")
# obama_face_encoding = face_recognition.face_encodings(obama_image)[0]

# Initialize some variables
face_locations = []
face_encodings = []

while True:
    # print("Capturing image.")
    # Grab a single frame of video from the RPi camera as a numpy array
    # camera.capture(output, format="rgb")
    rval, output = camera.read()
    output = cv2.flip(output, -1) # Flip vertically

    # Find all the faces and face encodings in the current frame of video
    face_locations = face_recognition.face_locations(output)
    # print("Found {} faces in image.".format(len(face_locations)))
    face_encodings = face_recognition.face_encodings(output, face_locations)

    # Loop over each face found in the frame to see if it's someone we know.
    name = []
    for face_encoding in face_encodings:
        # See if the face is a match for the known face(s)
        matches = face_recognition.compare_faces(known_face_encodings, face_encoding)
        for idx in range(len(matches)):
            if matches[idx]:
                name.append(known_names[idx])
            else:
                name.append("Unknown")

    i = 0
    for (top, right, bottom, left) in face_locations:
        cv2.rectangle(output, (left, top), (right, bottom), (0, 0, 255), 2)
        cv2.putText(output, name[i], (left + 6, bottom - 6), font, 1.0, (255, 255, 255), 1)
        i += 1

    cv2.imshow('Video', output)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cv2.destroyAllWindows()
