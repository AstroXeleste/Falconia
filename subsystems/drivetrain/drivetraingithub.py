import time
import curses
from adafruit_motorkit import MotorKit

# Initialize MotorKit
kit = MotorKit()

# Define motor speed (range: 0 to 1)
DEFAULT_SPEED = -1

def move_forward(speed=DEFAULT_SPEED):
    kit.motor3.throttle = speed
    kit.motor4.throttle = speed

def move_backward(speed=DEFAULT_SPEED):
    kit.motor3.throttle = -speed
    kit.motor4.throttle = -speed

def turn_left(speed=DEFAULT_SPEED):
    kit.motor3.throttle = -speed
    kit.motor4.throttle = speed

def turn_right(speed=DEFAULT_SPEED):
    kit.motor3.throttle = speed
    kit.motor4.throttle = -speed

def stop():
    kit.motor3.throttle = 0
    kit.motor4.throttle = 0

def keyboard_control(stdscr):
    stdscr.nodelay(1)  # Non-blocking input
    stdscr.timeout(100)  # Refresh every 100ms
    stdscr.addstr(0, 0, "Use WASD to move, Q to quit.")

    while True:
        key = stdscr.getch()

        if key == ord('w'):  # Forward
            move_forward()
            stdscr.addstr(1, 0, "Moving Forward  ")
        elif key == ord('s'):  # Backward
            move_backward()
            stdscr.addstr(1, 0, "Moving Backward ")
        elif key == ord('a'):  # Left
            turn_left()
            stdscr.addstr(1, 0, "Turning Left    ")
        elif key == ord('d'):  # Right
            turn_right()
            stdscr.addstr(1, 0, "Turning Right   ")
        elif key == ord('q'):  # Quit
            stop()
            break
        else:
            stop()
            stdscr.addstr(1, 0, "Stopping        ")

if __name__ == "__main__":
    curses.wrapper(keyboard_control)  # Handles setup and cleanup safely
