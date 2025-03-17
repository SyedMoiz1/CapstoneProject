import tkinter as tk
from tkinter import font
from screeninfo import get_monitors  # Get monitor details


class LogWindow:
    def __init__(self):
        """Initialize the Tkinter window in the main thread."""
        self.root = tk.Tk()
        self.root.title("Game Log")
        custom_font = font.Font(family="Helvetica", size=45)  # Change the font size as needed
        self.text_widget = tk.Text(self.root, wrap="word", height=100, width=200, font=custom_font)
        self.text_widget.pack()
        self.text_widget.insert("end", "Game log initialized...\n")
        self.move_to_second_monitor()
        

    def move_to_second_monitor(self):
        """Move the window to the second monitor and maximize it."""
        monitors = get_monitors()

        if len(monitors) > 1:  # Check if a second monitor exists
            second_monitor = monitors[1]  # Get the second monitor details

            # Get second monitor's resolution and position
            width, height = second_monitor.width, second_monitor.height
            x_position, y_position = second_monitor.x, second_monitor.y

            # Temporarily withdraw, set position, and show again
            self.root.withdraw()  # Hide window to prevent flickering
            self.root.geometry(f"{width}x{height}+{x_position}+{y_position}")  # Move and resize
            self.root.update_idletasks()  # Ensure window updates before showing
            self.root.deiconify()  # Show window again

            # Maximize instead of fullscreen
            self.root.state("zoomed")  # Windows maximize (Linux/macOS: use geometry instead)
        else:
            print("Second monitor not detected. Opening on the primary monitor.")
            self.root.state("zoomed")  # Open maximized on primary monitor

    def log_to_gui(self, message):
        """Safely update GUI from any thread using `after()`."""
        if self.root:
            self.root.after(0, self._update_gui, message)

    def _update_gui(self, message):
        """Internal method to update the Tkinter Text widget."""
        self.text_widget.delete("1.0", "end")  # Erase all text
        self.text_widget.insert("end", message + "\n")
        self.text_widget.see("end")  # Scroll to the latest message

    def run(self):
        """Ensure Tkinter runs in the main thread."""
        self.root.mainloop()
