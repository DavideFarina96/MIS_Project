# A Multisensory System Approach to Arm Movement Rehabilitation

- Filippo Nardin, filippo.nardin-1@studenti.unitn.it
- Davide Farina, davide.farina-1@studenti.unitn.it

## Abstract
There are several ways a patient can go back to moving his upper limbs after an accident or some other kind of issue. These rehabilitation tasks are performed with the help of doctors, which guide the patient through some motions in order to help the patient regain the ability to control the movements of the arms without feeling pain or discomfort.
Our system aims at simplifying this process while at the same time making it more effective, by using a 3D Virtual Reality Environment in which the patient is given some paths to follow with their hand. Through headphones and small vibration motors placed on the wrist of the user, audio and haptic feedback is provided, helping the patient in his movements by having a better knowledge of how s/he’s performing.
Although the system we created did not completely confirm our hypothesis, we believe that, with some additional work, a system such as this could really help in this field.

## How to setup

### Unity
- In folder `unity_proj` you can find the Unity3D project of our simulation. To run this, you need to install Unity3D 2019.2.15f1
- To run the project go in `unity_proj/Assets/Scenes/` and open `SampleScene.unity` with Unity3D
- From Unity3D, go to the Asset Store and install `Oculus Integration` and `extOSC - Open Sound Control`. These two assets are required to run the project correctly
- Oculus Quest: from Unity3D, build the project for the Oculus Quest (by setting the build target to Android)
- Oculus Rift S: connect an Oculus Rift S to the pc and simply run it from the engine

### Teensy
- In folder arduino_serial_communication_send_receive you can find the file to be uploaded to the Teensy
- The correct sensors should also be connected to the board. The correct pinout can be seen from the `.ino` file itself. Just one pressure sensor is used

### PureData
- In folder code_pd you can find the files needed to run the PureData code on the Raspberry Pi 4
- The main file is `MAIN_pi.pd`, and this is the file you should open from PureData

### Data Analysis
- To analyze the data gathered we wrote a python script. This script can be found in folder `data_analysis`
- To run the script, simply run `python analysis.py` in a console. 
- To correctly run the script, you need a folder called `logs` and, inside this folder, a folder for each user (`u1`, `u2`, ..., `u10`)
- These `.txt` files can be found in the zip file `logs.zip`
- The output are two graphs, called `Error.svg` and `Pressure.svg`

Note that the IP Addresses set in Unity3D and PureData are the ones we used.
- Raspberry Pi IP Address: `192.168.0.20`
- Oculus Quest IP Address: `192.168.0.15`
- WiFi network name: `MIS15_5GHz`
