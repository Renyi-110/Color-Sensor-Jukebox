# Jukebox.py
# Yixin Ren
# Thonny
# --- Imports -----------------------------------------------------
import RPi.GPIO as GPIO
import tkinter as tk
from tkinter import ttk, messagebox
import time
import threading

# --- GPIO/Hardware Setup -----------------------------------------------------
# Set the GPIO mode to BCM (Broadcom SOC channel numbers)
GPIO.setmode(GPIO.BCM)
# Disable warnings for GPIO operations
GPIO.setwarnings(False)
# Define GPIO pin mappings for the color sensor, buzzer, servos, and LEDs
COLOR_SENSOR = {'S0': 18, 'S1': 19, 'S2': 20, 'S3': 21, 'OUT': 17}
BUZZER_PIN = 23 # Pin for the buzzer
SERVO_DRAWER = 27 # Pin for the drawer servo
SERVO_POINTER = 22 # Pin for the pointer servo
LED_PINS = {'red': 25, 'green': 24, 'blue': 13, 'yellow': 6, 'white': 4} # LED pin mappings
# Setup GPIO pins for color sensor and other components
for pin in [COLOR_SENSOR['S0'], COLOR_SENSOR['S1'], COLOR_SENSOR['S2'],
COLOR_SENSOR['S3']]:
GPIO.setup(pin, GPIO.OUT) # Set color sensor pins as output
GPIO.setup(COLOR_SENSOR['OUT'], GPIO.IN) # Set output pin of color sensor as input
GPIO.setup(BUZZER_PIN, GPIO.OUT) # Set buzzer pin as output
GPIO.setup(SERVO_DRAWER, GPIO.OUT) # Set drawer servo pin as output
GPIO.setup(SERVO_POINTER, GPIO.OUT) # Set pointer servo pin as output
for pin in LED_PINS.values():
GPIO.setup(pin, GPIO.OUT) # Set LED pins as output
# Initialize PWM for servos to control their position
drawer_servo = GPIO.PWM(SERVO_DRAWER, 50) # 50Hz frequency for drawer servo
pointer_servo = GPIO.PWM(SERVO_POINTER, 50) # 50Hz frequency for pointer servo
drawer_servo.start(0) # Start drawer servo at 0 degrees
pointer_servo.start(0) # Start pointer servo at 0 degrees
# --- Color/Note Mapping ------------------------------------------------------
# Calibration thresholds for color detection
COLOR_THRESHOLDS = {

'red': ([60, 0, 0], [255, 80, 80]), # Red color range
'green': ([0, 60, 0], [80, 255, 80]), # Green color range
'blue': ([0, 0, 60], [80, 80, 255]), # Blue color range
'yellow': ([60, 60, 0], [255, 255, 80]), # Yellow color range
'white': ([180, 180, 180], [255, 255, 255]) # White color range
}
# Mapping of colors to musical notes and their frequencies
COLOR_NOTES = {
'red': ('C', 261.63), # C note frequency
'green': ('D', 293.66), # D note frequency
'blue': ('E', 329.63), # E note frequency
'yellow': ('F', 349.23), # F note frequency
'white': ('G', 392.00) # G note frequency
}
# Servo angles for pointing to colors
SERVO_POINTER_ANGLES = {
'red': 0, # Angle for red
'green': 45, # Angle for green
'blue': 90, # Angle for blue
'yellow': 135, # Angle for yellow
'white': 180 # Angle for white
}
# --- Helper Functions --------------------------------------------------------
def set_servo_angle(servo, angle):
"""
Set the angle of a servo motor.
Parameters:
servo (PWM): The PWM object controlling the servo.
angle (int): The angle to set the servo to (0-180 degrees).
"""
duty = angle / 18 + 2.5 # Convert angle to duty cycle
servo.ChangeDutyCycle(duty) # Set the duty cycle to move the servo
time.sleep(0.5) # Allow time for the servo to reach the position
servo.ChangeDutyCycle(0) # Stop sending signals to the servo
def pulseIn(pin, level, timeout=0.1):
"""
Measure the duration of a pulse on a GPIO pin.
Parameters:
pin (int): The GPIO pin number to read from.
level (int): The level to wait for (HIGH or LOW).
timeout (float): The maximum time to wait for the pulse.

Returns:
int: The duration of the pulse in microseconds, or 0 if timed out.
"""
t0 = time.time() # Start time
while GPIO.input(pin) != level: # Wait for the pin to reach the desired level
if time.time() - t0 > timeout: # Check for timeout
return 0 # Return 0 if timed out
t1 = time.time() # Time when the level is reached
while GPIO.input(pin) == level: # Wait for the pin to go low
if time.time() - t1 > timeout: # Check for timeout
break
t2 = time.time() # Time when the level goes low again
return (t2 - t1) * 1000000 # Return duration in microseconds
def read_color_sensor():
"""
Read the RGB values from the color sensor.
Returns:
list: A list containing the average red, green, and blue values.
"""
results = [] # List to store readings
for _ in range(3): # Take 3 readings for averaging
# Read Red
GPIO.output(COLOR_SENSOR['S2'], GPIO.LOW) # Set S2 and S3 for red
GPIO.output(COLOR_SENSOR['S3'], GPIO.LOW)
time.sleep(0.05) # Wait for sensor to stabilize
red = pulseIn(COLOR_SENSOR['OUT'], GPIO.LOW) # Read red value
# Read Green
GPIO.output(COLOR_SENSOR['S2'], GPIO.HIGH) # Set S2 and S3 for green
GPIO.output(COLOR_SENSOR['S3'], GPIO.HIGH)
time.sleep(0.05) # Wait for sensor to stabilize
green = pulseIn(COLOR_SENSOR['OUT'], GPIO.LOW) # Read green value
# Read Blue
GPIO.output(COLOR_SENSOR['S2'], GPIO.LOW) # Set S2 and S3 for blue
GPIO.output(COLOR_SENSOR['S3'], GPIO.HIGH)
time.sleep(0.05) # Wait for sensor to stabilize
blue = pulseIn(COLOR_SENSOR['OUT'], GPIO.LOW) # Read blue value
results.append((red, green, blue)) # Store the readings
# Average the readings
avg = [sum(x) / len(x) for x in zip(*results)] # Calculate average RGB values
return avg # Return the average RGB values

def classify_color(rgb):
"""
Classify the detected RGB values into a color.
Parameters:
rgb (list): A list containing the RGB values.
Returns:
str: The name of the detected color.
"""
for color, (low, high) in COLOR_THRESHOLDS.items(): # Check each color threshold
if all(l <= v <= h for v, l, h in zip(rgb, low, high)): # Check if RGB values are within
thresholds
return color # Return the detected color
# Fallback: pick the highest channel if no color matched
max_idx = rgb.index(max(rgb)) # Find the index of the maximum value
return ['red', 'green', 'blue'][max_idx] # Return the corresponding color
# --- Main Application Class --------------------------------------------------
class MusicComposerApp:
def __init__(self, root):
"""
Initialize the Music Composer application.
Parameters:
root (Tk): The root window for the application.
"""
self.root = root # Store the root window
self.root.title("Pi Music Composer") # Set the window title
self.current_frame = None # Current frame being displayed
self.song_length = 0 # Length of the song
self.bpm = 120 # Beats per minute for the song
self.song_sequence = [] # Sequence of notes in the song
self.is_drawer_open = False # State of the drawer (open/closed)
self.current_note = 0 # Index of the current note being inserted
self.buzzer_pwm = GPIO.PWM(BUZZER_PIN, 440) # Initialize buzzer PWM at 440Hz
self.setup_welcome_frame() # Setup the welcome frame
def clear_frame(self):
"""
Clear the current frame from the root window.
"""
if self.current_frame:
self.current_frame.destroy() # Destroy the current frame to clear it
# --- Servo Control ---
def open_drawer(self):

"""
Open the drawer by setting the servo angle.
"""
set_servo_angle(drawer_servo, 90) # Set servo to 90 degrees to open the drawer
self.is_drawer_open = True # Update the state to indicate the drawer is open
self.update_note_buttons() # Update the state of note buttons
def close_drawer(self):
"""
Close the drawer by setting the servo angle.
"""
set_servo_angle(drawer_servo, 0) # Set servo to 0 degrees to close the drawer
self.is_drawer_open = False # Update the state to indicate the drawer is closed
self.update_note_buttons() # Update the state of note buttons
def point_to_color(self, color):
"""
Point the servo to the specified color.
Parameters:
color (str): The color to point to.
"""
angle = SERVO_POINTER_ANGLES[color] # Get the angle for the specified color
set_servo_angle(pointer_servo, angle) # Set the pointer servo to the corresponding
angle
# --- Color Detection ---
def detect_color(self):
"""
Detect the color using the color sensor and light up the corresponding LED.
Returns:
str: The detected color.
"""
rgb = read_color_sensor() # Read RGB values from the color sensor
color = classify_color(rgb) # Classify the detected RGB values into a color
# Light up LED for feedback
for led_color, pin in LED_PINS.items():
GPIO.output(pin, GPIO.HIGH if led_color == color else GPIO.LOW) # Turn on the
corresponding LED
# Move pointer servo to the detected color
self.point_to_color(color) # Point the servo to the detected color
time.sleep(0.3) # Allow time for the pointer to move
for pin in LED_PINS.values():
GPIO.output(pin, GPIO.LOW) # Turn off all LEDs after a short delay
return color # Return the detected color
# --- Buzzer ---

def play_note(self, frequency, duration):
"""
Play a note using the buzzer.
Parameters:
frequency (float): The frequency of the note to play.
duration (float): The duration to play the note for (in seconds).
"""
self.buzzer_pwm.ChangeFrequency(frequency) # Change the frequency of the buzzer
self.buzzer_pwm.start(50) # Start the buzzer at 50% duty cycle
time.sleep(duration) # Play for the specified duration
self.buzzer_pwm.stop() # Stop the buzzer after the duration
def play_song(self):
"""
Play the composed song based on the stored sequence of notes.
"""
if not self.song_sequence: # Check if there are no notes to play
return # Exit if the song sequence is empty
duration = 60 / self.bpm # Calculate duration of each note based on BPM
for note, freq in self.song_sequence: # Iterate through the song sequence
self.play_note(freq, duration) # Play each note
time.sleep(0.05) # Small delay between notes
# --- GUI Frames ---
def setup_welcome_frame(self):
"""
Setup the welcome frame of the application.
"""
self.clear_frame() # Clear any existing frame
self.current_frame = tk.Frame(self.root) # Create a new frame for the welcome screen
tk.Label(self.current_frame, text="Welcome to Pi Music Composer!", font=("Arial",
22)).pack(pady=20) # Welcome label
tk.Button(self.current_frame, text="Write Song", font=("Arial", 16),
command=self.setup_settings_frame).pack(pady=10) # Button to write a song
tk.Button(self.current_frame, text="How to Use", font=("Arial", 16),
command=self.show_instructions).pack(pady=10) # Button to show instructions
tk.Button(self.current_frame, text="Exit", font=("Arial", 16),
command=self.root.destroy).pack(pady=10) # Button to exit the application
self.current_frame.pack(expand=True) # Pack the current frame to display it
def setup_settings_frame(self):
"""
Setup the settings frame for selecting number of notes and BPM.
"""
self.clear_frame() # Clear any existing frame
self.current_frame = tk.Frame(self.root) # Create a new frame for settings

tk.Label(self.current_frame, text="Number of Notes:", font=("Arial", 16)).pack(pady=5)
# Label for notes
self.note_slider = ttk.Scale(self.current_frame, from_=1, to=10, orient=tk.HORIZONTAL)
# Slider for number of notes
self.note_slider.set(5) # Set default value to 5
self.note_slider.pack() # Pack the slider
self.note_label = tk.Label(self.current_frame, text="5", font=("Arial", 14)) # Label to
display selected notes
self.note_label.pack() # Pack the label
# Update label when slider is moved
self.note_slider.bind("<Motion>", lambda e:
self.note_label.config(text=str(int(self.note_slider.get()))))
tk.Label(self.current_frame, text="BPM:", font=("Arial", 16)).pack(pady=5) # Label for
BPM
self.bpm_slider = ttk.Scale(self.current_frame, from_=60, to=180,
orient=tk.HORIZONTAL) # Slider for BPM
self.bpm_slider.set(120) # Set default BPM to 120
self.bpm_slider.pack() # Pack the slider
self.bpm_label = tk.Label(self.current_frame, text="120", font=("Arial", 14)) # Label to
display selected BPM
self.bpm_label.pack() # Pack the label
# Update label when slider is moved
self.bpm_slider.bind("<Motion>", lambda e:
self.bpm_label.config(text=str(int(self.bpm_slider.get()))))
tk.Button(self.current_frame, text="Next", font=("Arial", 14),
command=self.setup_compose_frame).pack(pady=10) # Button to proceed to

composition
tk.Button(self.current_frame, text="Home", font=("Arial", 14),
command=self.setup_welcome_frame).pack(pady=5) # Button to return to

welcome screen
self.current_frame.pack(expand=True) # Pack the current frame to display it
def setup_compose_frame(self):
"""
Setup the compose frame for entering notes.
"""
self.song_length = int(self.note_slider.get()) # Get the number of notes from the slider
self.bpm = int(self.bpm_slider.get()) # Get the BPM from the slider
self.song_sequence = [] # Initialize the song sequence
self.current_note = 0 # Reset the current note index
self.clear_frame() # Clear any existing frame
self.current_frame = tk.Frame(self.root) # Create a new frame for composition
self.note_buttons = [] # List to hold note buttons
tk.Label(self.current_frame, text="Compose Your Song", font=("Arial", 18)).grid(row=0,
column=0, columnspan=5, pady=10) # Title label

for i in range(self.song_length): # Create buttons for each note
btn = tk.Button(self.current_frame, text="Press to insert note", width=20, height=2,
command=lambda idx=i: threading.Thread(target=self.insert_note,

args=(idx,)).start())
btn.grid(row=1 + i // 5, column=i % 5, padx=5, pady=5) # Place buttons in a grid
self.note_buttons.append(btn) # Add button to the list
# Drawer controls
tk.Button(self.current_frame, text="Open Drawer", width=15,
command=lambda:

threading.Thread(target=self.open_drawer).start()).grid(row=3, column=0, pady=10) #
Button to open drawer
tk.Button(self.current_frame, text="Close Drawer", width=15,
command=lambda:

threading.Thread(target=self.close_drawer).start()).grid(row=3, column=1, pady=10) #
Button to close drawer
# Home button
tk.Button(self.current_frame, text="Home", width=15,
command=self.setup_welcome_frame).grid(row=3, column=2, pady=10) #

Button to return to welcome screen
self.play_btn = tk.Button(self.current_frame, text="Play", width=15, state=tk.DISABLED,
command=lambda: threading.Thread(target=self.play_song).start()) #

Button to play the song
self.play_btn.grid(row=3, column=3, pady=10) # Place play button in the grid
self.update_note_buttons() # Update the state of note buttons
self.current_frame.pack(expand=True) # Pack the current frame to display it
def update_note_buttons(self):
"""
Update the state of the note buttons based on the current note index.
"""
for i, btn in enumerate(self.note_buttons): # Iterate through note buttons
if i == self.current_note and not self.is_drawer_open: # Enable button if it's the
current note and drawer is closed
btn.config(state=tk.NORMAL)
else:
btn.config(state
btn.config(state=tk.DISABLED) # Disable other buttons
if self.current_note == self.song_length: # If all notes have been inserted
self.play_btn.config(state=tk.NORMAL) # Enable the play button to play the song
else:
self.play_btn.config(state=tk.DISABLED) # Otherwise, disable the play button
def insert_note(self, index):
"""
Insert a note into the song sequence based on the detected color.

Ensures notes are inserted in order and the drawer is closed before detecting color.
Parameters:
index (int): The index of the note button pressed.
"""
if self.is_drawer_open:
messagebox.showerror("Drawer Open", "Please close the drawer before inserting a
note.") # Require drawer to be closed
return
if index != self.current_note:
messagebox.showerror("Order Error", "Please insert notes in order.") # Enforce
sequential note insertion
return
color = self.detect_color() # Detect color from sensor
if color not in COLOR_NOTES:
messagebox.showerror("Color Error", "Unrecognized color. Try again.") # Notify if
color unrecognized
return
note, freq = COLOR_NOTES[color] # Map color to note and frequency
self.song_sequence.append((note, freq)) # Append note to song sequence
self.note_buttons[index].config(text=note, bg=color, state=tk.DISABLED) # Update
button with note and disable it
self.current_note += 1 # Move to next note index
self.update_note_buttons() # Refresh button states
def show_instructions(self):
"""
Show a popup message box with instructions on how to use the application.
"""
msg = (
"1. Click 'Write Song'.\n"
"2. Choose number of notes and BPM, then 'Next'.\n"
"3. For each note:\n"
" - Place a colored chip in the drawer.\n"
" - Close the drawer.\n"
" - Press the corresponding 'Press to insert note' button.\n"
" - The system will detect the color, show the note, and move the pointer.\n"
"4. After all notes are entered, press 'Play' to hear your song.\n"
"5. Use 'Home' to return to the main menu."
)
messagebox.showinfo("How to Use", msg) # Display the instructions dialog
# --- Main Execution ----------------------------------------------------------
if __name__ == "__main__":
try:
root = tk.Tk() # Create the main Tkinter window
root.geometry("900x600") # Set the window size to 900x600 pixels

app = MusicComposerApp(root) # Initialize the MusicComposerApp with the window
root.mainloop() # Enter the Tkinter event loop to run the GUI application
finally:
GPIO.cleanup() # Clean up all GPIO settings to leave pins in a safe state when the
program exits
