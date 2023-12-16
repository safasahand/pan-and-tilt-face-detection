import cv2
import time
import requests
import numpy as np
import traceback
from serial import Serial, SerialException
from cvzone.FaceDetectionModule import FaceDetector

# Set your Arduino's serial port and baud rate
serial_port = 'COM5'  # Change this to your Arduino's serial port
baud_rate = 9600  # Make sure it matches the baud rate in your Arduino code

camera_url = 'http://192.168.27.25/capture'
detector = FaceDetector()

arduino = None  # Initialize arduino variable

try:
    arduino = Serial(serial_port, baud_rate, timeout=1)
except SerialException as e:
    print(f"Serial Exception: {e}")
    exit()
except Exception as e:
    print(f"Error: {e}")
    exit()

while True:
    try:
        response = requests.get(camera_url)
        img_arr = np.array(bytearray(response.content), dtype=np.uint8)
        img = cv2.imdecode(img_arr, -1)

        img, bboxs = detector.findFaces(img)

        if bboxs:
            face = bboxs[0]  # Assuming only one face is detected

            face_bbox = face['bbox']  # Access the 'bbox' key in the face dictionary

            face_center_x = (face_bbox[0] + face_bbox[2]) // 2
            face_center_y = (face_bbox[1] + face_bbox[3]) // 2

            frame_height, frame_width, _ = img.shape

            if face_center_y < frame_height // 3:
                arduino.write(b'u')  # Move tilt up
            elif face_center_y > frame_height // 3:
                arduino.write(b'd')  # Move tilt down
            #else:
                #arduino.write(b's')  # Stop tilt movement

            if face_center_x < frame_width // 3:
                arduino.write(b'l')  # Move pan left
            elif face_center_x > frame_width // 3:
                arduino.write(b'r')  # Move pan right
            #else:
                #time.sleep(3)
                #arduino.write(b's')  # Stop pan movement

        else:
            #time.sleep(3)
            arduino.write(b's')
            print("No face detected.")

        cv2.imshow("image", img)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    except IndexError:
        print("No face detected.")

    except Exception as e:
        print(f"Error: {e}")
        print(f"Type: {type(e)}")
        print(traceback.format_exc())
        break

if arduino:
    arduino.close()
cv2.destroyAllWindows()
