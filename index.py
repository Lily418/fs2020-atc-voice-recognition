from PIL import Image
import pytesseract

import re
import azure.cognitiveservices.speech as speechsdk
from sentence_transformers import SentenceTransformer, util
import os
from pywinauto.application import Application

model = SentenceTransformer('all-MiniLM-L6-v2')

atc1 = pytesseract.image_to_string(Image.open('grey-ATC3.png'), lang='eng', config=r'--psm 6')
# print(pytesseract.image_to_string(Image.open('ATC2.png'), lang='eng', config=r'--psm 6'))
# print(pytesseract.image_to_string(Image.open('ATC3.png'), lang='eng', config=r'--psm 6'))

# print(pytesseract.get_languages(config=''))

print(atc1)

p = re.compile(r'^([0-9]+)\s([A-Z \W]+)\b', re.MULTILINE)

# print(atc1)
# print("-----")
matches = p.findall(atc1)
print(matches)

def from_file():
    speech_config = speechsdk.SpeechConfig(subscription=os.environ["AZURE_FS2020_ATC_SPEECH_KEY"], region="uksouth")
    audio_input = speechsdk.AudioConfig(filename="sayagain.wav")
    speech_recognizer = speechsdk.SpeechRecognizer(speech_config=speech_config, audio_config=audio_input)
    
    result = speech_recognizer.recognize_once_async().get()
    print(result.text)
    return result.text

# from_file()

voice = "Say again."

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