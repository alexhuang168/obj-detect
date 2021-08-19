# DSR Object Detection
The DSR Object Detection system was designed to notify the DSR disinfection program of any humans detected in the room during disinfection to turn off disinfection methods for safety reasons.

## Setup (from scratch)
### What you'll need
For each DSR, you will need:
- 1x Jetson Nano board (Model B01)
- 1x MicroSD card (min. 64GB) & card reader
- 1x 5V 4A barrel jack power supply
- 2x WaveShare IMX219-IR cameras
- 2x Camera ribbon cables
- Computer
- DSR

See [this link](https://developer.nvidia.com/embedded/learn/get-started-jetson-nano-devkit) for how to set up the Jetson Nano MicroSD card. Once the OS is installed, boot up the Nano and:
1. Open the terminal
2. Clone this repo (home directory preferred)

    `git clone https://github.com/globaldws/dsr-object-detection.git`

3. Login to your GlobalDWS GitHub if prompted
4. Change directory to 'dsr-object-detection' `cd dsr-object-detection`
5. Make sure both cameras are connected to the Nano, and run `python3 dsr_detection.py`

If you encounter any errors, see 'Troubleshooting' section below.

If the program runs without any errors, we now want to set this script to execute automatically when the Nano boots up.
    * To do this, launch the 'Startup Applications' program from the Applications folder
    * Click *Add*
    * Name the program 'dsr' and paste the following line where it says 'Command:'
    `python3 /home/globaldws/dsr-object-detection/dsr_detection.py`

---

## How to use & testing
The dsr-object-detection program should run automatically when the Jetson Nano boots up.
If you wish to run the program manually, you must first kill the current program if it is running (Note: you can uncheck the 'dsr' startup program in the Startup Applications preference during testing). To kill a running program, you must first be logged in to the Nano, connected to a monitor with a keyboard and mouse. A running dsr-object-detection program will show up on the screen as it requires the display. You can close it if it is running.

To manually run the dsr-object-detection program, open a Terminal window and navigate to the project folder (/home/dsr-object-detection).

Here, run `python3 dsr_detection.py` - the camera windows should open and output printed to the terminal.

Note that if you run dsr_detection.py through ssh, the program is not likely to operate properly as it requires a UI.

---


## Troubleshooting
### Testing the cameras
After connecting the cameras, we can test if they are connected properly by running the following command: 

`$ gst-launch-1.0 nvarguscamerasrc sensor_id=0 ! nvoverlaysink`

Where *sensor_id* is the camera we are connecting to, starting at 0.


### Clearing the camera pipeline
If you run into issues, the first thing to try is cleaning the camera pipeline by running the following command

`$ sudo systemctl restart nvargus-daemon`

This can especially happen if the program was haulted or interrupted.
