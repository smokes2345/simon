#!/usr/bin/env python3
import logging
import time
import sys
from threading import Timer, Thread, Event

from respeaker import Microphone
from pixel_ring import pixel_ring
from gpiozero import LED
from speech_recognition import Microphone, Recognizer, WaitTimeoutError, UnknownValueError

import pyalmond
import pyttsx3

logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)

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

class Assistant():

    def __init__(self, name,  mic):
        self.name = name
        self.mic = mic
        self.recognizer = Recognizer()
        self.awake = False

    def listen(self):
        with self.mic:
            self.recognizer.adjust_for_ambient_noise(self.mic, 2)
            print("Starting listener...")
        self.stop = self.recognizer.listen_in_background(self.mic, self._proc_audio)

    def stop(self):
        raise RuntimeError("Attempted to stop assistant before starting it")

    def wake_up(self):
        self.awake = True
        def _timeout():
            self.awake = False
        timer = Timer(30, _timeout)
        timer.start()

    def _proc_audio(self, recog, audio):
        try:
            # decoded = recog.recognize_sphinx(audio, show_all=True)
            # txt = decoded.hyp().hypstr
            txt = recog.recognize_google(audio, show_all=True)
            print(f"recognized utterance: {txt}")
        except UnknownValueError as e:
            # txt = recog.recognize_google(audio)
            print("Did not recognize utterance")
            # print(txt)
        if self.name in txt:
            self.wake_up()
        if self.awake and not txt.endswith(self.name):
            print(f"Sending commands: {txt}")
            pixel_ring.think()
            # send command to HA here
            pixel_ring.off()
            self.awake = False
        else:
            print(f"Not awake or name was give without command")
        return


#def task(quit_event):
#    #mic = Microphone(quit_event=quit_event)
#    pass
def get_mic():
    mic_index = None
    for i, microphone_name in enumerate(Microphone.list_microphone_names()):
        if 'seeed' in microphone_name:
            mic_index = i
            print("Using microphone {}".format(microphone_name))
            break
    if not mic_index:
        print("Could not find a proper microphone")
        exit()
    return Microphone(device_index=mic_index)

def task(quit_event):
    with Microphone(device_index=mic_index, quit_event=quit_event) as mic:
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

    simon = Assistant('simon', get_mic())
    quit_event = Event()
    #thread = Thread(target=task, args=(quit_event,))
    #thread.daemon = True
    #thread.start()
    pixel_ring.set_brightness(9)
    simon.listen()
    tts.startLoop()
    print("Starting main loop")
    while True:
        try:
            time.sleep(1)
        except KeyboardInterrupt:
            print('Quit')
            quit_event.set()
            simon.stop()
            break
    time.sleep(1)

if __name__ == '__main__':
    main()

