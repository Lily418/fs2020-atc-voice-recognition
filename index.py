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
from threading import Thread
import concurrent.futures

understood_speech = None
understood_commands = None
ocr_understood = None

# Code Timers
pressf8 = None
presscommand = None
speechunderstoodtime = None
ocrunderstoodtime= None
matchescreatedtime = None

keyboard_controller = Controller()

recording = False
fs = 44100  # Sample rate
seconds = 30  # Duration of recording
myrecording = None
start = None
datetimeForLog = None

model = SentenceTransformer('all-MiniLM-L6-v2')

commandRegex = re.compile(r'^([0-9]+)\s([A-Z0-9\W]+?)$', re.MULTILINE)

app = Application(backend="uia").connect(title_re=".*Microsoft Flight Simulator.*")


# Turn the Blue button background to white
def process_screenshot(screenshot): 
    screenshot_cropped = ImageOps.crop(screenshot, border=18)
    atc_invert = ImageOps.invert(screenshot_cropped)
    width = atc_invert.size[0] 
    height = atc_invert.size[1] 

    for i in range(0,width):
        for j in range(0,height):
            data = atc_invert.getpixel((i,j))
            if data[0] == 255 and data[1] == 75 and data[2] == 0:
                atc_invert.putpixel((i,j),(255, 255, 255))
    return atc_invert

def get_commands():
    startImageCaptureTime = time.perf_counter()
    atc_image = app.window(handle=pywinauto.findwindows.find_window(title="ATC")).capture_as_image()
    endImageCaptureTime = time.perf_counter()
    print(f"Time from startImageCaptureTime to endImageCaptureTime {endImageCaptureTime - startImageCaptureTime:0.4f} seconds")

    proccessScreenshotTime = time.perf_counter()
    proccessed_atc_image = process_screenshot(atc_image)
    endProccessScreenshotTime = time.perf_counter()
    
    print(f"Time from proccessScreenshotTime to endProccessScreenshotTime {endProccessScreenshotTime - proccessScreenshotTime:0.4f} seconds")

    global datetimeForLog 
    atc_image.save(Path('.') / "atc-archive" / (str(datetimeForLog) + ".png"), "PNG")

    ocrStart = time.perf_counter()
    atc1 = pytesseract.image_to_string(proccessed_atc_image, lang='eng', config=r'--psm 6')
    ocrEnd = time.perf_counter()

    print(f"Time from ocrStart to ocrEnd {ocrEnd - ocrStart:0.4f} seconds")

    global ocrunderstoodtime
    ocrunderstoodtime = time.perf_counter()

    matches = commandRegex.findall(atc1)
    print("found matches")
    global matchescreatedtime
    matchescreatedtime = time.perf_counter()
    print(f"Time from ocr understood time to matchescreatedtime {matchescreatedtime - ocrunderstoodtime:0.4f} seconds")

    global ocr_understood
    ocr_understood = atc1
    global understood_commands
    understood_commands = matches
    

def with_speech_and_matches():
    global understood_speech
    global understood_commands
    global ocr_understood
    global recording

    print("understood_speech" + understood_speech)

    

    global datetimeForLog
    log_file = open(Path('.') / "atc-archive" / (datetimeForLog + ".txt"),'w')
    log_file.write("OCR_UNDERSTOOD:\n" + ocr_understood + "\nSPEECH_UNDERSTOOD:\n"+understood_speech + "\n REGEX MATCHES:\n"+str(understood_commands)+"\n")
 

    print("understood_commands", understood_commands)

    if(len(understood_commands) == 0):
        print("No matches")
        recording = False
        # log_file.close()
        return None


    encodeUnderstoodSpeech =  time.perf_counter()
    
    voice_embeddings = model.encode([understood_speech])


    max_score = 0
    command_number = None
    command_label = None

    for command in understood_commands:
        print("command" + str(command))
        command_embeddings = model.encode([command[1].upper()])
        cosine_scores = util.pytorch_cos_sim(voice_embeddings, command_embeddings)
        command_score = cosine_scores[0].item()

        if command_score > max_score:
            command_label = command[1].upper()
            max_score = command_score
            command_number = command[0]

    encodeUnderstoodSpeechFinish =  time.perf_counter()
    print(f"Time from encodeUnderstoodSpeech to encodeUnderstoodSpeechFinish {encodeUnderstoodSpeechFinish - encodeUnderstoodSpeech:0.4f} seconds")


    print("Selected " + command_number + ". " + command_label)
    log_file.write("Selected " + command_number + ". " + command)
    log_file.close()
    print("Press " + str(command_number))

    global pressf8
    global presscommand
    presscommand = time.perf_counter()

    print(f"Time from f8 to response {presscommand - pressf8:0.4f} seconds")


    keyboard_controller.press(command_number)
    time.sleep(0.1)
    keyboard_controller.release(command_number)

    recording = False


def from_mic():
    speech_config = speechsdk.SpeechConfig(subscription=os.environ["AZURE_FS2020_ATC_SPEECH_KEY"], region="uksouth")
    speech_recognizer = speechsdk.SpeechRecognizer(speech_config=speech_config)
    
    print("Speak into your microphone.")
    result = speech_recognizer.recognize_once()
    print("Result text: " + result.text)
    global speechunderstoodtime
    speechunderstoodtime = time.perf_counter()
    print(f"Time from f8 to speech understood time {speechunderstoodtime - pressf8:0.4f} seconds")
    global understood_speech
    understood_speech = result.text

def on_press(key):
    try:
        global recording, start
        if key == keyboard.Key.f8 and recording == False:
            global pressf8
            pressf8 = time.perf_counter()

            global datetimeForLog 
            datetimeForLog = str(math.floor(datetime.datetime.now().timestamp()))
            print("Calling from_mic()")
            recording = True
            t1 = Thread(target=from_mic)
            t2 = Thread(target=get_commands)
                        
            # start the threads
            t1.start()
            t2.start()

            # wait for the threads to complete
            t1.join()
            t2.join()

            with_speech_and_matches()
        if key == keyboard.Key.esc:
            return False
            
    except AttributeError:
        print('special key {0} pressed'.format(
            key))

# Collect events until released
with keyboard.Listener(
        on_press=on_press) as listener:
    listener.join()