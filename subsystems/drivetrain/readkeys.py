import curses
from adafruit_motorkit import MotorKit
import time

global MTR_1_FORWARD
global MTR_2_FORWARD

MTR_2_FORWARD = -1.0 # in negative direction because of reversed charges on motor
MTR_2_FORWARD = 1.0

kit = MotorKit()

def forward():
    kit.motor2.throttle = MTR_2_FORWARD
    kit.motor1.throttle = MTR_1_FORWARD

def backward():
    kit.motor2.throttle = -MTR_2_FORWARD
    kit.motor1.throttle = -MTR_1_FORWARD

def left():
    kit.motor2.throttle = 1.0

def right():
    kit.motor2.throttle = 1.0

def stop():
    kit.motor2.throttle = 0
    kit.motor1.throttle = 0


def keyboard_to_motor(stdscr):
    # Clear screen and set up for non-blocking input
    stdscr.clear()
    curses.curs_set(0)  # Hide the cursor
    stdscr.nodelay(1)   # Set non-blocking input
    curses.noecho()     # Disable the echo of characters typed
    stdscr.timeout(100) # Set a small timeout (in milliseconds) for getch()

    while True:
        key = stdscr.getch()  # Get the pressed key (non-blocking)

        # If no key is pressed, `getch()` returns -1
        if key == -1:
            continue

        # Detect arrow keys
        if key == curses.KEY_LEFT:
            stdscr.addstr(0, 0, "You Pressed left!")
        elif key == curses.KEY_RIGHT:
            stdscr.addstr(0, 0, "You Pressed right!")
        elif key == curses.KEY_DOWN:
            stdscr.addstr(0, 0, "You Pressed down!")
            stop()
        elif key == curses.KEY_UP:
            stdscr.addstr(0, 0, "You Pressed up!")
            forward()
        elif key == curses.KEY_BACKSPACE:
            # ADD READING FUNCTIONALITY HERE
            stdscr.addstr(0, 0, "You are reading")
        elif key == 27:  # Escape key to exit
            break

        stdscr.refresh()  # Refresh the screen to show updated text
        stdscr.clear()    # Clear the screen for the next update


# Run the curses application
while True:
     kit.motor2.throttle = MTR_2_FORWARD
     kit.motor1.throttle = MTR_2_FORWARD