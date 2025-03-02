# VisLink Guide
![Logo](/vislink_logo.png)
## Project Story
It is without a doubt that computers have played a pivotal role within the lives of billions of people worldwide. However, as powerful as a tool computers are, most require physical interaction in order to access them - creating a barrier for those who suffer from mobility impairments due to limited hand functionality. There have been hardware configured specifically to cater to these individuals in the past, however, most of these extensions are very expensive and not everyone is able to afford them. As a solution, we envisioned VisLink - a hands free control software rather than hardware which only requires a working webcam (built into most laptops) to use, promoting accessibility to computers to those with mobility disabilities both physically and financially.\
## Installation
To start, clone the git repository
```
git clone https://github.com/Neiljya/head-tracking-mouse-movement.git
```
Then, to install dependencies, run the command
```
pip install -r requirements.txt
```
Additionally, ensure your Python version is 3.9-3.12 for MediaPipe backend
```
python --version
```
## Usage
To start VisLink, run this command in the project directory:
```
python main.py
```

After a few seconds, a window like the following should appear:\
![first window](/readmeAssets/screen1.png)\

Once the tool loads, a window like the following will appear\
![second window](/readmeAssets/screen2.png)\
In this window, you can change some of the tool's properties.\
Sensitivity: The amount to scale mouse movement so you can move your head either less or more\
Blink interval: The max amount of time between blinks to be counted as double or triple blinks\
Countdown: Number of seconds to start the tool from pressing start\

Once you have configured your settings, press start to take you to the tool's launch window:\
![third_window](/readmeAssets/screen3.png)\
Here, you can change the settings one last time before starting the tool. When you press start, a countdown will appear, after which the tool will start.

![fourth window](/readmeAssets/screen4.png)

From here, the tool has a wide variety of different functionalities:
- Clearly say "Start Webcam" as an alternative to pressing the start button
- Move your head to move the cursor
- Blink twice or clearly say "Left click" to click where the pointer is
- Blink three times or clearly say "Right click" to right click where the pointer is
- Blink four times to double click where the pointer is
- Clearly say "increase sensitivity" to increase the sensitivity by 1
- Clearly say "decrease sensitivity" to decrease the sensitivity by 1
- Clearly say "Start typing" to enter typing mode
- Once in typing mode, clearly say what you want to type, and it will be sent to the keyboard
- Clearly say "Stop typing" to exit typing mode
- Clearly say "Exit" or click the red button to quit the tool
