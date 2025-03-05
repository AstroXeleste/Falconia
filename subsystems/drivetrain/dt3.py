import time
import curses
from adafruit_motorkit import MotorKit
from collections import deque

# Initialize MotorKit
kit = MotorKit()

# Define motor speed (range: 0 to 1)
DEFAULT_SPEED = -1

# Command queue to store buffered inputs
command_queue = deque()

def stop():
    kit.motor3.throttle = 0
    kit.motor4.throttle = 0

def move_forward(speed=DEFAULT_SPEED, t=0.5):
    kit.motor3.throttle = speed
    kit.motor4.throttle = speed
    time.sleep(t)
    stop()

def move_backward(speed=DEFAULT_SPEED, t=0.5):
    kit.motor3.throttle = -speed
    kit.motor4.throttle = -speed
    time.sleep(t)
    stop()

def turn_right(speed=DEFAULT_SPEED, t=0.5):
    kit.motor3.throttle = -speed
    kit.motor4.throttle = speed
    time.sleep(t)
    stop()

def turn_left(speed=DEFAULT_SPEED, t=0.5):
    kit.motor3.throttle = speed
    kit.motor4.throttle = -speed
    time.sleep(t)
    stop()


def keyboard_control(stdscr):
    stdscr.nodelay(1)  # Non-blocking input
    stdscr.timeout(100)  # Refresh every 100ms
    stdscr.addstr(0, 0, "Use WASD to move, Q to quit.")

    while True:
        key = stdscr.getch()

        if key == ord('w'):  # Forward
            stdscr.addstr(1, 0, "Moving Forward  ")
            time.sleep(8)
            move_forward()
        elif key == ord('s'):  # Backward
            stdscr.addstr(1, 0, "Moving Backward  ")
            time.sleep(8)
            move_backward()
        elif key == ord('a'):  # Left
            stdscr.addstr(1, 0, "Moving Left  ")
            time.sleep(8)
            turn_left()
        elif key == ord('d'):  # Right
            stdscr.addstr(1, 0, "Moving Right  ")
            time.sleep(8)
            turn_right()
        elif key == ord('q'):  # Quit
            stop()
            break
        elif key == ord('e'):
            stop()
        # else:
        #     stop()
        #     stdscr.addstr(1, 0, "Stopping        ")

if __name__ == "__main__":
    curses.wrapper(keyboard_control)  # Handles setup and cleanup safely
