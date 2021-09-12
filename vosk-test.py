from vosk import Model, KaldiRecognizer, SetLogLevel
from pathlib import Path
import sounddevice as sd
import queue

model = Model("vosk-model")
q = queue.Queue()

device_info = sd.query_devices(sd.default.device, 'input')
samplerate = int(device_info['default_samplerate'])
dump_fn = open("dump.wav", "wb")


def callback(indata, frames, time, status):
    """This is called (from a separate thread) for each audio block."""
    if status:
        print(status, file=sys.stderr)
    q.put(bytes(indata))

with sd.RawInputStream(samplerate=samplerate, blocksize = 8000, dtype='int16',
                        channels=1, callback=callback, device="MacBook Pro Microphone"):
        print('#' * 80)
        print('Press Ctrl+C to stop the recording')
        print('#' * 80)

        rec = KaldiRecognizer(model, samplerate)
        while True:
            data = q.get()
            if rec.AcceptWaveform(data):
                print(rec.Result())
            else:
                print(rec.PartialResult())
            if dump_fn is not None:
                dump_fn.write(data)

