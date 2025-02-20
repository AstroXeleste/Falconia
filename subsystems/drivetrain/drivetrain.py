import curses

def main(stdscr):
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
        elif key == curses.KEY_UP:
            stdscr.addstr(0, 0, "You Pressed up!")
        elif key == 27:  # Escape key to exit
            break

        stdscr.refresh()  # Refresh the screen to show updated text
        stdscr.clear()    # Clear the screen for the next update

# Run the curses application
curses.wrapper(main)
