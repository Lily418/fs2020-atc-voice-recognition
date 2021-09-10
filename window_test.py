from pywinauto.application import Application
from pynput import mouse, keyboard
import pywinauto
import sounddevice as sd
from scipy.io.wavfile import write
from timeit import default_timer
import math

# sd.wait()  # Wait until recording is finished
# write('output.wav', fs, myrecording)  # Save as WAV file 



# app = Application(backend="uia").connect(title_re=".*Microsoft Flight Simulator.*")
# print(app.window(handle=pywinauto.findwindows.find_window(title="ATC")).capture_as_image().save("./atc.png", "PNG"))


recording = False
fs = 44100  # Sample rate
seconds = 30  # Duration of recording
myrecording = None
start = None

def on_press(key):
    try:
        global recording, start
        if key == keyboard.Key.f12 and recording == False:
            start = default_timer()
            recording = True
            global myrecording
            myrecording = sd.rec(int(seconds * fs), samplerate=fs, channels=2)
    except AttributeError:
        print('special key {0} pressed'.format(
            key))

def on_release(key):
    if key == keyboard.Key.f12:
        # Stop listener
        sd.stop()
        print(myrecording)
        global start
        duration = default_timer() - start
        print("recording time" + str(duration))
        print("bits to wrangle" + str(duration * fs))
        myrecording_trimmed = myrecording[0:math.ceil(duration * fs)]
        write('output.wav', fs, myrecording_trimmed)  # Save as WAV file 
        return False

# Collect events until released
with keyboard.Listener(
        on_press=on_press,
        on_release=on_release) as listener:
    listener.join()

