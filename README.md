# bii-gesture-control
Gesture window control for PR Building Interaction Interfaces

# Dependencies
- the application only works on Windows
- other platforms are supported, but cannot move windows
- Python 3.8
- [Autohotkey](https://www.autohotkey.com/)
- Python packages
  - PySimpleGUI
  - ahk
  - mediapipe
  - opencv-python

# Run the Application 
- run `python win_force.py`
- click on 'minimize' to close the big window, in the lower right corner the emoji indicator appears
- a click on the miniature window in the lower right corner will open the big window again

# Detected gestures
- move your hand to the middle of the x or y axis
- after a sound is played and/or the hand emoji is present in the emoji indicator
  - move your hand up or down: the focused window is snapped up or down (analog to `windows + UP/DOWN` on the keyboard)
  - move your hand left or right: the focused window is snapped to the left or right (analog to `windows + LEFT/RIGHT` on the keyboard)
  - form a fist gesture to cancel the current detection of your hand
