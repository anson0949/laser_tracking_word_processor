from gtts import gTTS
import os
import pyglet
import sys
import time
from googletrans import Translator

def playSound(text, language):
    t = Translator()
    print(text)
    trans = gTTS(text=t.translate(text, dest=language).text, lang="zh-tw")
    trans.save("t.mp3")
    player = pyglet.media.Player()
    player.queue(pyglet.resource.media("t.mp3"))
    player.play()
    os.remove("t.mp3")
