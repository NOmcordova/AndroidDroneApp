from typing import Any, Dict
import requests
from time import sleep
import cv2
import numpy as np


class DJIControlClient:

    # Connect to the server, using the ip and port.
    def __init__(self, ip: str, port: int = 8080) -> None:
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
    def photo(self, name) -> Dict[str, Any]:
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


# convert nv21 file to jpg
def convert(w, h, name):
    width = int(w)
    height = int(h)
    if width <= 0 or height <= 0:
        raise Exception('Invalid dimentions!')
    src = np.fromfile("photo.nv21", dtype='uint8').reshape(int(height + height / 2), width)
    dst = cv2.cvtColor(src, cv2.COLOR_YUV2BGR_NV21)
    cv2.imwrite(name, dst)



