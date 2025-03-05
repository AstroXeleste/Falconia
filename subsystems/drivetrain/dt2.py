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

def execute_command():
    while True:
        if command_queue:
            command = command_queue.popleft()
            command()  # Execute stored command
            time.sleep(8)  # 8-second delay between commands
        else:
            time.sleep(0.1)  # Prevent busy-waiting

def keyboard_control(stdscr):
    stdscr.nodelay(1)  # Non-blocking input
    stdscr.timeout(100)  # Refresh every 100ms
    stdscr.addstr(0, 0, "Use WASD to move, Q to quit.")
    
    while True:
        key = stdscr.getch()
        
        if key == ord('w'):  # Forward
            command_queue.append(move_forward)
            stdscr.addstr(1, 0, "Buffered: Move Forward  ")
        elif key == ord('s'):  # Backward
            command_queue.append(move_backward)
            stdscr.addstr(1, 0, "Buffered: Move Backward ")
        elif key == ord('a'):  # Left
            command_queue.append(turn_left)
            stdscr.addstr(1, 0, "Buffered: Turn Left    ")
        elif key == ord('d'):  # Right
            command_queue.append(turn_right)
            stdscr.addstr(1, 0, "Buffered: Turn Right   ")
        elif key == ord('q'):  # Quit
            command_queue.append(stop)
            break
        
        stdscr.refresh()

if __name__ == "__main__":
    import threading
    execution_thread = threading.Thread(target=execute_command, daemon=True)
    execution_thread.start()
    curses.wrapper(keyboard_control)  # Handles setup and cleanup safely
