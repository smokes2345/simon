#!/usr/bin/env python3
import logging
import time
from threading import Thread, Event

from respeaker import Microphone
from pixel_ring import pixel_ring
from gpiozero import LED
from speech_recognition import Microphone, Recognizer

import pyalmond
import pyttsx3

power = LED(5)
power.on()

name = 'simon'

tts = pyttsx3.init()


def get_greeting():
    from random import choice
    greetings = [
            "How can I help?",
            ]
    return choice(greetings)

class Assistant(obj):


    def __init__(self, name,  mic):
        self.name = name
        self.mic = mic
        self.recognizer = Recognizer()
        self.awake = False

    def listen(self)
        self.recognizer.adjust_for_ambient_noise(self.mic, 2)
        self.stop = self.recognizer.listen_in_background(self.mic, self._proc_audio)

    def _proc_audio(self, recog, audio):
        txt = recog.recognize_sphinx(audio)
        if txt == self.name:
            try:
                self.stop()
                tts.say(get_greeting())
                pixel_ring.listen()
                cmd_aud = recog.listen(self.mic, timeout=10)
            except speech_recognition.WaitTimeoutError:
                pixel_ring.off()
                return
            pixel_ring.think()
            cmd_txt = recog.recognize_sphinx(cmd_aud)


def task(quit_event):
    #mic = Microphone(quit_event=quit_event)
    mic_index = None
    for i, microphone_name in enumerate(Microphone.list_microphone_names()):
        if 'seeed' in microphone_name:
            mic_index = i
            print("Using microphone {}".format(microphone_name))
            break
    if not mic_index:
        print("Could not find a proper microphone")
        exit()
    with Microphone(device_index=mic_index) as mic:
        recognizer = Recognizer()
        while not quit_event.is_set():
            pixel_ring.off()
            print("Listening for keyword")
            data = recognizer.listen(source=mic)
            kw_text = recognizer.recognize_sphinx(data)
            print("Heard '{}' while listening for keyword".format(kw_text))
            if kw_text == name:
                print('Wake up')
                pixel_ring.listen()
                data = recognizer.listen(mic)
                pixel_ring.think()
                text = recognizer.recognize_sphinx(data)
                print('Done listening')
                pixel_ring.off()
                if text:
                    print('Recognized {}'.format(text))
                    tts.say(text)
                    #tts.runAndWait()

def main():
    logging.basicConfig(level=logging.DEBUG)

    quit_event = Event()
    thread = Thread(target=task, args=(quit_event,))
    thread.daemon = True
    thread.start()
    pixel_ring.set_brightness(9)
    tts.startLoop()
    print("Starting main loop")
    while True:
        try:
            time.sleep(1)
        except KeyboardInterrupt:
            print('Quit')
            quit_event.set()
            break
    time.sleep(1)

if __name__ == '__main__':
    main()
