from PIL import Image, ImageOps
import pytesseract

import re
import azure.cognitiveservices.speech as speechsdk
from sentence_transformers import SentenceTransformer, util
import os
from pywinauto.application import Application
from pynput import keyboard
from pynput.keyboard import Key, Controller
import pywinauto
import sounddevice as sd
from scipy.io.wavfile import write
from timeit import default_timer
import time
import datetime
from pathlib import Path
import math 

keyboard_controller = Controller()

recording = False
fs = 44100  # Sample rate
seconds = 30  # Duration of recording
myrecording = None
start = None

model = SentenceTransformer('all-MiniLM-L6-v2')

commandRegex = re.compile(r'^([0-9]+)\s([A-Z0-9\W]+?)$', re.MULTILINE)



# Turn the Blue button background to white
def process_screenshot(screenshot): 
    atc_invert = ImageOps.invert(screenshot)
    width = atc_invert.size[0] 
    height = atc_invert.size[1] 

    for i in range(0,width):
        for j in range(0,height):
            data = atc_invert.getpixel((i,j))
            if data[0] == 255 and data[1] == 75 and data[2] == 0:
                atc_invert.putpixel((i,j),(255, 255, 255))
    return atc_invert
    

def with_speech(understood_speech):
    global recording

    app = Application(backend="uia").connect(title_re=".*Microsoft Flight Simulator.*")
    atc_image = app.window(handle=pywinauto.findwindows.find_window(title="ATC")).capture_as_image()
    proccessed_atc_image = process_screenshot(atc_image)
    proccessed_atc_image.save(Path('.') / "atc-archive" / (str(math.floor(datetime.datetime.now().timestamp())) + ".png"), "PNG")
    atc1 = pytesseract.image_to_string(proccessed_atc_image, lang='eng', config=r'--psm 6')



    matches = commandRegex.findall(atc1)
    print("found matches")
    
    if(len(matches) == 0):
        print("No matches")
        recording = False
        return None


    voice = understood_speech
    voice_embeddings = model.encode([voice])


    max_score = 0
    command_number = None
    command = None

    for match in matches:
        command_embeddings = model.encode([match[1].upper()])
        cosine_scores = util.pytorch_cos_sim(voice_embeddings, command_embeddings)
        command_score = cosine_scores[0].item()

        if command_score > max_score:
            command = match[1].upper()
            max_score = command_score
            command_number = match[0]


    print("Selected " + command_number + ". " + command)
    print("Press " + str(command_number))
    keyboard_controller.press(command_number)
    time.sleep(0.1)
    keyboard_controller.release(command_number)

    recording = False


def from_mic():
    speech_config = speechsdk.SpeechConfig(subscription=os.environ["AZURE_FS2020_ATC_SPEECH_KEY"], region="uksouth")
    speech_recognizer = speechsdk.SpeechRecognizer(speech_config=speech_config)
    
    print("Speak into your microphone.")
    result = speech_recognizer.recognize_once_async().get()
    print("Understood speech: " + result.text)
    with_speech(result.text)

def on_press(key):
    try:
        global recording, start
        if key == keyboard.Key.f8 and recording == False:
            print("Calling from_mic()")
            recording = True
            from_mic()
            
    except AttributeError:
        print('special key {0} pressed'.format(
            key))

# Collect events until released
with keyboard.Listener(
        on_press=on_press) as listener:
    listener.join()