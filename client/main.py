from ultralytics import YOLO
from typing import Any, Dict
import requests
from time import sleep
import cv2
import numpy as np
import math


class DJIControlClient:

    # Connect to the server, using the ip and port.
    def __init__(self, ip: str, port: int) -> None:
        self.ip = ip
        self.port = port

        self.server_addr = f"http://{self.ip}:{self.port}"

        r = requests.get(url=self.server_addr)

        assert r.content == b"Connected"

    def makeReqAndReturnJSON(self, route: str) -> Dict[str, Any]:
        r = requests.get(url=f"{self.server_addr}{route}")
        return r.json()

    # Take off
    def takeOff(self) -> Dict[str, Any]:
        return self.makeReqAndReturnJSON(f'/TakeOff')

    # requests a photo, with format nv21
    def camerastream(self) -> Dict[str, Any]:
        return self.makeReqAndReturnJSON('/CameraStream')

    # Initialize the camera stream (call this method in the begging if you want to take photos)
    def startcamerastream(self) -> Dict[str, Any]:
        return self.makeReqAndReturnJSON('/StartCameraStream')

    # Terminate the camera stream
    def stopcamerastream(self) -> Dict[str, Any]:
        return self.makeReqAndReturnJSON('/StopCameraStream')

    # Land
    def land(self) -> Dict[str, Any]:
        for i in range(10):
            self.makeReqAndReturnJSON('/Land')
            sleep(1)
            self.moveup(40, 1)
            self.moveup(-660, 7)
        return self.makeReqAndReturnJSON('/Land')

    # Enable the virtual stick (call this method in the begging if you wand to move the drone)
    def enable(self) -> Dict[str, Any]:
        return self.makeReqAndReturnJSON('/Enable')

    # Disable the virtual stick
    def disable(self) -> Dict[str, Any]:
        return self.makeReqAndReturnJSON('/Disable')

    # Rotate the camera to a 90 degree angle
    def cameradown(self) -> Dict[str, Any]:
        return self.makeReqAndReturnJSON('/CameraDown')

    # Rotate the camera to a 0 degree angle
    def cameraup(self) -> Dict[str, Any]:
        return self.makeReqAndReturnJSON('/CameraUp')

    # Move up (or down if param is negative).
    # Time represents the time of the movement in secs.
    # Param represents the velocity in the z axis (-660 to 660)
    def moveup(self, param, time) -> Dict[str, Any]:
        time = round(1000 * time)
        return self.makeReqAndReturnJSON(f'/MoveUp/{param}/{time}')

    # Rotate the camera to a given angle
    def rotatecamera(self, angle) -> Dict[str, Any]:
        return self.makeReqAndReturnJSON(f'/RotateCamera/{angle}')

    # Move forward (or backwards if param is negative).
    # Time represents the time of the movement in secs.
    # Param represents the velocity in the y axis (-660 to 660)
    # Right represents the velocity in the x axis (-660 to 660)- could be used for corrections
    def moveforward(self, forward, right, time) -> Dict[str, Any]:
        time = round(1000 * time)
        print(forward, right, time)
        return self.makeReqAndReturnJSON(f'/MoveForward/{forward}/{right}/{time}')

    # Rotate to the right (or left if param is negative).
    # Time represents the time of the movement in secs.
    # Param represents the velocity of the rotation (-660 to 660)
    def rotate(self, param, time) -> Dict[str, Any]:
        time = round(1000 * time)
        return self.makeReqAndReturnJSON(f'/Rotate/{param}/{time}')

    # Initialize the drone for the algorithm.
    def initialize(self) -> Dict[str, Any]:
        self.enable()
        self.startcamerastream()
        self.camerastream()
        return self.cameradown()

    # Move right (or left if param is negative).
    # Time represents the time of the movement in secs.
    # Param represents the velocity in the x axis (-660 to 660)
    def movesideways(self, param, time) -> Dict[str, Any]:
        time = round(1000 * time)
        return self.makeReqAndReturnJSON(f'/MoveSideways/{param}/{time}')

    # Take a photo and save it as a jpg file.
    # Name is the path and name where the photo should be saved.
    def photo(self,name) -> Dict[str, Any]:
        pic = self.camerastream()
        photo = pic["state"]
        for i in range(len(photo)):
            if photo[i] < 0:
                photo[i] += 256
        photo = bytes(photo)
        with open("photo.nv21", "wb") as bin_file:
            bin_file.write(photo)
        convert(pic["width"], pic["height"], name)
        return pic

    # Centralize above the jeep.
    # Assumes You can see the jeep when you call this method.
    def centralize(self):
        counter = 0
        i=0
        while counter < 4:
            self.photo("c_photo"+ str(i) +".jpg")
            result = photo_detection("c_photo"+ str(i) +".jpg", "res_c_photo"+ str(i) +".jpg")
            i += 1
            if result != -1:
                counter = 0
                x_1, y_1, x_2, y_2, score, class_id = result
                avg_X = (x_1 + x_2) / 2
                avg_y = (y_1 + y_2) / 2
                if 340 < avg_y and avg_y < 380 and avg_X < 660 and 620 < avg_X:
                    return 1
                elif y_1 < 10:
                    self.moveforward(2, 0, 3)
                elif x_1 < 10:
                    self.moveforward(0, 2, 3)
                elif y_2 > 710:
                    self.moveforward(-2, 0, 3)
                elif x_2 > 1270:
                    self.moveforward(0, -2, 3)
                else:
                    height = 720 * 32 / (y_2 - y_1)
                    width = 1280 * 40 / (x_2 - x_1)
                    print("width: ", width)
                    print("height: ", height)
                    dist_x = (avg_X - 640) * width / 1280
                    print("dist_x: ", dist_x)
                    dist_y = (-avg_y + 360) * height / 720
                    print("dist_y: ", dist_y)
                    if abs(dist_x) < 9 and abs(dist_y) < 7:
                        return 1
                    print("move right", math.copysign(2, dist_x))
                    self.moveforward(0, int(math.copysign(2, dist_x)), abs(dist_x / 12))
                    sleep(0.3)
                    print("move forward", math.copysign(2, dist_y))
                    self.moveforward(int(math.copysign(2, dist_y)), 0, abs(dist_y / 12))
            else:
                counter += 1
        return -1

    # Scans the room for the jeep
    def find_the_robot(self):
        for i in range(10):
            self.photo("ftr_photo"+ str(i) +".jpg")
            result = photo_detection("ftr_photo"+ str(i) +".jpg", "res_ftr_photo"+ str(i) +".jpg")
            if result != -1:
                return True
            self.moveforward(4, i % 2, 2.7)
        return False

# convert nv21 file #name to jpg
# w,h are the width and the height of the photo
def convert(w, h, name):
    width = int(w)
    height = int(h)
    if width <= 0 or height <= 0:
        raise Exception('Invalid dimentions!')
    src = np.fromfile("photo.nv21", dtype='uint8').reshape(int(height + height / 2), width)
    dst = cv2.cvtColor(src, cv2.COLOR_YUV2BGR_NV21)
    cv2.imwrite(name, dst)


def photo_detection(file, dst):
    img = cv2.imread(file)
    results = model(img)[0]
    for result in results.boxes.data.tolist():
        x_1, y_1, x_2, y_2, score, class_id = result
        print(result)
        if (score > 0.4):
            image = cv2.rectangle(img, (int(x_1), int(y_1)), (int(x_2), int(y_2)), (0, 255, 0), 4)
            cv2.imwrite(dst, image)
            return result
        else:
            return -1
    return -1


model = YOLO("C:\\Users\\dorni\\Documents\\Ody year 5\\Robotics- drone\\yolov8_test\\best.pt")
drone = DJIControlClient("172.20.10.4", 8080)
drone.initialize()
drone.takeOff()
sleep(5)
drone.moveup(30, 4)
sleep(0.3)
if drone.find_the_robot():
    print("Found you!")
    if drone.centralize() == 1:
        print("YO!!!")
        sleep(0.3)
        drone.moveup(-30, 4)
        sleep(2)
        drone.moveforward(-4, 0, 5)
    else:
        print("you suck!")
else:
    print(":(")

drone.land()
drone.disable()
