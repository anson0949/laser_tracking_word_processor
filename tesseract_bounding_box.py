import pytesseract
from PIL import Image
import cv2
import sys
from multiprocessing.pool import ThreadPool
from threading import Thread
import time
from math import sqrt
import enchant

class Character():
    def __init__(self, character, top_left, bottom_right):
        self.character = character
        self.top_left = top_left
        self.bottom_right = bottom_right

    def __repr__(self):
        return self.character

class Word():
    def __init__(self, word = '', top_left = (0,0), bottom_right = (0,0)):
        self.word = word
        self.top_left = top_left
        self.bottom_right = bottom_right

    def __repr__(self):
        return self.word

class ReturnThread(Thread):
    def __init__(self, group=None, target=None, name=None,
                 args=(), kwargs={}, Verbose=None):
        Thread.__init__(self, group, target, name, args, kwargs)
        self._return = None

    def run(self):
        if self._target is not None:
            self._return = self._target(*self._args,
                                                **self._kwargs)
    def join(self):
        Thread.join(self)
        return self._return

def getBounds(image):
    """Returns image with bounding boxes"""
    height, width, _ = image.shape
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    ##Threads
    t1 = ReturnThread(target=pytesseract.image_to_string, kwargs={'image':gray})
    t2 = ReturnThread(target=pytesseract.image_to_boxes, kwargs={'image':gray})
    t1.start()
    t2.start()
    words = t1.join()
    words = words.split()
    bounds = t2.join()


    ##Store the characters in a list
    bounds = bounds.split()
    characters = []
    temp = []
    for i in range(len(bounds)-1):
        if( i%6 == 0 ):
            character = bounds[i]
            top_left = (int(bounds[i+1]), height-int(bounds[i+2]))
            bottom_right = (int(bounds[i+3]), height-int(bounds[i+4]))
            characters.append(Character(character, top_left, bottom_right))
            
    ##Convert characters into words with bounds
    word_bounds = []
    d = enchant.Dict("en_GB")
    for w in words:
        word = []
        if d.check(w):
            try:
                for i in range(len(w)):
                    word.append(characters.pop(0))            
                word_bounds.append(Word(w, word[0].top_left, word[-1].bottom_right))
            except:
                pass

    return word_bounds
    
            
def drawBounds(image, bounds):
    ##Draw bounding boxes onto image
    for i in bounds:
        cv2.rectangle(image, i.top_left, i.bottom_right, (0,255,0), 3)
    return image


def getWord(bounds, center):
    """Returns the word closest to the laser"""
    distance = float('inf')
    word = ""
    for w in bounds:
        bound_center = ((w.top_left[0]+w.bottom_right[0])/2, (w.top_left[1]+w.bottom_right[1])/2)
        temp_d = sqrt(abs(bound_center[0]-center[0])**2+abs(bound_center[1]-center[1])**2)
        if temp_d < distance:
            distance = temp_d
            word = w.word
    
    return word


