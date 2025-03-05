import time
import curses
from adafruit_motorkit import MotorKit

# Initialize MotorKit
kit = MotorKit()

# Define motor speed (range: 0 to 1)
DEFAULT_SPEED = -1
DELAY_SECONDS = 0.2  # Reduced delay for continuous movement

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
    stdscr.timeout(10)  # Reduced timeout for responsiveness
    stdscr.addstr(0, 0, "Use WASD to move, Q to quit.")

    last_action_time = {} # dictionary to store last action time for each key
    for key_ord in [ord('w'), ord('a'), ord('s'), ord('d')]:
        last_action_time[key_ord] = 0

    while True:
        key = stdscr.getch()
        current_time = time.time()

        if key in last_action_time:
            if current_time - last_action_time[key] >= DELAY_SECONDS:
                last_action_time[key] = current_time #update the last action time.
                if key == ord('w'):
                    move_forward()
                    stdscr.addstr(1, 0, "Moving Forward    ")
                elif key == ord('s'):
                    move_backward()
                    stdscr.addstr(1, 0, "Moving Backward   ")
                elif key == ord('a'):
                    turn_left()
                    stdscr.addstr(1, 0, "Turning Left      ")
                elif key == ord('d'):
                    turn_right()
                    stdscr.addstr(1, 0, "Turning Right     ")
            else:
                pass #do nothing, waiting for delay to finish.
        elif key == ord('q'):
            stop()
            break
        elif key != -1:
            stop()
            stdscr.addstr(1, 0, "Stopping          ")
        else:
            stop()
            stdscr.addstr(1, 0, "Stopping          ")

if __name__ == "__main__":
    curses.wrapper(keyboard_control)
