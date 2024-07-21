# Workshop in Robot Motion Planning
The software’s goal is to drop an object on a small jeep using a drone.
## Requirements
1. Android Studio Chipmunk 2021.2.1 Patch 1 (might work with other versions as well).
2. Python.
3. Ultralytics.
## Equipment
1. DJI mini 3 drone.
2. Dropping mechanism made using Arduino Uno.
3. DJI RC-N1.
4. 9V battery.
5. Type C to type C cable.
6. Android phone with version 13+.
7. Cellotape. 
8. Zip tie.
9. Computer.
10. Elevation for the front legs of the drone.
11. Jeep.
## Installing the application
1. Download the repository.
2. In Android Studio, open the folder Mobile-SDK-Android-V5-dev-sdk-main\SampleCode-V5\android-sdk-v5-as.
3. Follow the instructions under “Generate an App Key” https://developer.dji.com/doc/mobile-sdk-tutorial/en/quick-start/run-sample.html.
4. Install the appliction on the phone https://developer.android.com/codelabs/basic-android-kotlin-compose-connect-device?continue=https%3A%2F%2Fdeveloper.android.com%2Fcourses%2Fpathways%2Fandroid-basics-compose-unit-1-pathway-2%23codelab-https%3A%2F%2Fdeveloper.android.com%2Fcodelabs%2Fbasic-android-kotlin-compose-connect-device#0.
## Connecting the mechanism to the drone
1. Connect the mechanism to the drone using the cellotape and the zip ties.
2. Connect the battery to the top of the drone.
## Preparing the environment
1. Connect the elevation to the floor, and place the drone on it.
2. Place the jeep vertically to the drone and infront of it in a radius of about a meter to the sides.
## Running the program
1. Turn the drone and the RC on by pressing and then holding the power button.
2. Connect the phone to the RC using the cable.
3. Check the phone’s IP address, and write it at the desinated place in the Python code.
4. Open the MSDK aircraft appliction on the phone.
5. In the application, Press Testing Tools->Virtual Stick->Take Off.
6. Connect the battery to the Arduino. This starts a 40s timer, so make sure to take off before it ends.
7. Run the Python code.
