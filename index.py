from PIL import Image, ImageOps
import pytesseract

import re
import sentence_transformers
from sentence_transformers import SentenceTransformer, util
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
import json
import vosk
from vosk import Model, KaldiRecognizer
from pathlib import Path
import sounddevice as sd
import queue
import os

vosk_model = Model("vosk-model")

device_info = sd.query_devices(sd.default.device, 'input')
samplerate = int(device_info['default_samplerate'])
rec = KaldiRecognizer(vosk_model, samplerate)

menu_item_map = json.loads(open(Path(".") / "menu_item_map.json",'r', encoding="utf8").read())

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

commandRegex = re.compile(r'^([0-9]+) ([A-Z0-9\W]+?)$', re.MULTILINE)

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
    app = Application(backend="uia").connect(title_re=".*Microsoft Flight Simulator.*")
    startImageCaptureTime = time.perf_counter()
    atc_image = app.window(handle=pywinauto.findwindows.find_window(title="ATC")).capture_as_image()
    endImageCaptureTime = time.perf_counter()
    print(f"Time from startImageCaptureTime to endImageCaptureTime {endImageCaptureTime - startImageCaptureTime:0.4f} seconds")

    proccessScreenshotTime = time.perf_counter()
    proccessed_atc_image = process_screenshot(atc_image)
    endProccessScreenshotTime = time.perf_counter()
    
    print(f"Time from proccessScreenshotTime to endProccessScreenshotTime {endProccessScreenshotTime - proccessScreenshotTime:0.4f} seconds")


    loggingFolder = Path('.') / "atc-archive"
    
    if not loggingFolder.exists():
        os.makedirs(loggingFolder)

    global datetimeForLog 
    atc_image.save(loggingFolder / (str(datetimeForLog) + ".png"), "PNG")

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

    loggingFolder = Path('.') / "atc-archive"
    
    if not loggingFolder.exists():
        os.makedirs(loggingFolder)

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

        # For commands like acknowledgement expected speech is dissimilar
        # from the label text
        expected_speech = [command[1].upper()] + (menu_item_map.get(command[1].upper()) or [])
        expected_speech_embeddings = map(lambda x: model.encode([x]), expected_speech)
        
        for expected_speech_embedding in expected_speech_embeddings:
            cosine_scores = util.pytorch_cos_sim(voice_embeddings, expected_speech_embedding)
            expected_speech_score = cosine_scores[0].item()

            if expected_speech_score > max_score:
                command_label = command[1].upper()
                max_score = expected_speech_score
                command_number = command[0]

    encodeUnderstoodSpeechFinish =  time.perf_counter()
    print(f"Time from encodeUnderstoodSpeech to encodeUnderstoodSpeechFinish {encodeUnderstoodSpeechFinish - encodeUnderstoodSpeech:0.4f} seconds")


    print("Selected " + command_number + ". " + command_label)
    log_file.write("Selected " + command_number + ". " + command_label)
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

    q = queue.Queue()

    def callback(indata, frames, time, status):
        q.put(bytes(indata))

    with sd.RawInputStream(samplerate=samplerate, blocksize = 8000, dtype='int16',
                        channels=1, callback=callback):
        print("Speak into your microphone.")

        result = None
        while result == None:
            data = q.get()
            if rec.AcceptWaveform(data):
                result = json.loads(rec.Result()).get('text')

        global speechunderstoodtime
        speechunderstoodtime = time.perf_counter()
        print(f"Time from f8 to speech understood time {speechunderstoodtime - pressf8:0.4f} seconds")
        global understood_speech
        understood_speech = result

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
            
    except AttributeError:
        print('special key {0} pressed'.format(
            key))

print("Listening")

# Collect events until released
with keyboard.Listener(
        on_press=on_press) as listener:
    listener.join()