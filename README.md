# VisLink Usage Guide
![Logo](/vislink_logo.png)
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
After a few seconds, a window like the following should appear.
![first window](/readmeAssets/screen1.png)
Once the tool loads, a window like the following will appear
![second window](/readmeAssets/screen2.png)
In this window, you can change some of the tool's properties. 
Sensitivity: The amount to scale mouse movement so you can move your head either less or more
Blink interval: The max amount of time between blinks to be counted as double or triple blinks
Countdown: Number of seconds to start the tool from pressing start

Once you have configured your settings, press start to take you to the tool's launch window:
![third_window](/readmeAssets/screen2.png)
