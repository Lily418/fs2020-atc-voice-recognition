from PIL import Image, ImageOps
import pytesseract

import re
import azure.cognitiveservices.speech as speechsdk
from sentence_transformers import SentenceTransformer, util
import os
from pywinauto.application import Application
from pynput import mouse, keyboard
from pynput.keyboard import Key, Controller
import pywinauto
import sounddevice as sd
from scipy.io.wavfile import write
from timeit import default_timer
import math

keyboard_controller = Controller()

recording = False
fs = 44100  # Sample rate
seconds = 30  # Duration of recording
myrecording = None
start = None

model = SentenceTransformer('all-MiniLM-L6-v2')


def with_speech(understood_speech):
    global recording

    app = Application(backend="uia").connect(title_re=".*Microsoft Flight Simulator.*")
    atc_image = app.window(handle=pywinauto.findwindows.find_window(title="ATC")).capture_as_image()
    ImageOps.invert(atc_image).save("./atc.png", "PNG")

    atc1 = pytesseract.image_to_string(Image.open('atc.png'), lang='eng', config=r'--psm 6')

    # print(pytesseract.get_languages(config=''))

    p = re.compile(r'^([0-9]+)\s([A-Z0-9\W]+?)$', re.MULTILINE)

    # print(atc1)
    # print("-----")
    matches = p.findall(atc1)
    

    print(atc1)
    
    if(len(matches) == 0):
        print("No matches")
        recording = False
        return None

    # def from_file():
    #     speech_config = speechsdk.SpeechConfig(subscription=os.environ["AZURE_FS2020_ATC_SPEECH_KEY"], region="uksouth")
    #     audio_input = speechsdk.AudioConfig(filename="output.wav")
    #     speech_recognizer = speechsdk.SpeechRecognizer(speech_config=speech_config, audio_config=audio_input)
        
    #     result = speech_recognizer.recognize_once_async().get()
    #     print(result)
    #     print(result.text)
    #     return result.text


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


    print(command_number + ". " + command)
    print("Press " + str(command_number))
    keyboard_controller.press(command_number)
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

# def on_release(key):
#     return None
#     if key == keyboard.Key.f8:
#         # Stop listener
#         sd.stop()
#         global start
#         duration = default_timer() - start
#         print("recording time "  + str(duration))
#         myrecording_trimmed = myrecording[0:math.ceil(duration * fs)]
#         write('output.wav', fs, myrecording_trimmed * 20)  # Save as WAV file 
#         print("wrote output.wav")
#         return False

# Collect events until released
with keyboard.Listener(
        on_press=on_press) as listener:
    listener.join()