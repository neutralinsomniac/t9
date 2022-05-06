#!/usr/bin/env python3

import time
import sys
from os.path import exists
from getkey import getkey, keys

ERASE_LINE = "\x1b[2K"
UNDERLINE_START = u"\u001b[4m"
UNDERLINE_END = u"\u001b[0m"

# load dictionary
if len(sys.argv) != 2:
    print("usage: {} <dict.txt>".format(sys.argv[0]))
    sys.exit(1)

class WordNotFoundException(Exception):
    pass

class T9Engine():
    T9 = {'.': 1, ',': 1, '!': 1, '?': 1,
          ':': 1, '-': 1, '\'': 1,
          '(': 1, ')': 1, ';': 1, '[': 1, ']': 1,
          'a': 2, 'b': 2, 'c': 2,
          'd': 3, 'e': 3, 'f': 3,
          'g': 4, 'h': 4, 'i': 4,
          'j': 5, 'k': 5, 'l': 5,
          'm': 6, 'n': 6, 'o': 6,
          'p': 7, 'q': 7, 'r': 7, 's': 7,
          't': 8, 'u': 8, 'v': 8,
          'w': 9, 'x': 9, 'y': 9, 'z': 9}

    def __init__(self):
        self._lookup = {} # our dictionary
        self._cur = self._lookup # where we're sitting in the dictionary
        self._history = [] # breadcrumb pointers of the path we've taken through the dictionary
        self._completion_len = 0 # number of characters in the current completion state
        self._completion_choice = 0 # index into current 'words' array

    def add_word(self, word):
        cur = self._lookup
        for c in word:
            num = self.T9[c.lower()]
            if num not in cur:
                cur[num] = {}
            cur = cur[num]
        if "words" not in cur:
            cur["words"] = []
        if word not in cur["words"]:
            cur["words"].append(word)

    def load_dict(self, filename):
        with open(filename, "r") as dictionary:
            for word in dictionary.readlines():
                self.add_word(word.strip())

    def add_digit(self, digit):
        if digit not in self._cur:
            raise WordNotFoundException
        self._completion_len += 1
        self._history.append(self._cur)
        self._cur = self._cur[digit]
        self._completion_choice = 0
        return self.get_completion()

    def backspace(self):
        self._completion_choice = 0
        if len(self._history) > 0:
            self._cur = self._history.pop()
            self._completion_len -= 1
        return self.get_completion()

    def get_completion(self):
        if self._completion_len == 0:
            return ""
        candidate = self._cur
        while candidate:
            if 'words' in candidate:
                return candidate['words'][self._completion_choice % len(candidate['words'])]
            for key in iter(candidate):
                if key != "words":
                    candidate = candidate[key]
                    break

    def next_completion(self):
        if self._completion_len == 0:
            return

        if "words" not in self._cur or (self._completion_choice + 1) >= len(self._cur['words']):
            raise WordNotFoundException

        self._completion_choice += 1

    def reset_completion(self):
        self._completion_choice = 0

    def new_completion(self):
        self._cur = self._lookup
        self._history.clear()
        self._completion_choice = 0
        self._completion_len = 0

    def get_cur_completion_len(self):
        return self._completion_len

def recalculate_state():
    global t9_engine
    global line
    global doing_punctuation_stuff

    word = line.split(" ")[-1]
    doing_punctuation_stuff = False
    for c in word:
        if T9Engine.T9[c.lower()] == 1 and not doing_punctuation_stuff:
            t9_engine.new_completion()
            doing_punctuation_stuff = True
        t9_engine.add_digit(T9Engine.T9[c.lower()])
    if t9_engine.get_cur_completion_len() != 0:
        # init the engine with the word
        word_to_match = line[-1*t9_engine.get_cur_completion_len():]
        line = line[:-1*t9_engine.get_cur_completion_len()]
        try:
            while t9_engine.get_completion() != word_to_match:
                t9_engine.next_completion()
        except WordNotFoundException:
            pass

t9_engine = T9Engine()

if exists("user_dict.txt"):
    print("loading user_dict.txt...")
    start = time.time()
    t9_engine.load_dict("user_dict.txt")
    print("loaded in {}s".format(time.time() - start))

print("loading {}...".format(sys.argv[1]))
start = time.time()
t9_engine.load_dict(sys.argv[1])
print("loaded in {}s".format(time.time() - start))

line = ""

doing_punctuation_stuff = False

word_not_found = False

while True:
    completion = t9_engine.get_completion()
    completion_len = t9_engine.get_cur_completion_len()
    completion_left = completion[:completion_len]
    completion_right = completion[completion_len:]
    print(ERASE_LINE + "\r" + line + UNDERLINE_START + completion_left + UNDERLINE_END + completion_right + ("?" if word_not_found else ""), end='')
    key = getkey()

    if key == "Q":
        break

    # for using a-z and period instead of numbers
    try:
        if not key.isdecimal():
            key = str(T9Engine.T9[key.lower()])
    except KeyError:
        pass

    if key in "123456789":
        word_not_found = False
        if key in "1":
            if not doing_punctuation_stuff:
                doing_punctuation_stuff = True
                line += t9_engine.get_completion()
                t9_engine.new_completion()
        try:
            t9_engine.add_digit(int(key))
        except WordNotFoundException:
            if not doing_punctuation_stuff:
                word_not_found = True
            pass
    elif key == keys.TAB:
        if word_not_found:
            t9_engine.reset_completion()
            word_not_found = False
        else:
            try:
                t9_engine.next_completion()
            except WordNotFoundException:
                if not doing_punctuation_stuff:
                    word_not_found = True
                else:
                    t9_engine.reset_completion()
                pass
    elif key == "0" or key == keys.SPACE:
        word_not_found = False
        line += t9_engine.get_completion() + " "
        t9_engine.new_completion()
        doing_punctuation_stuff = False
    elif key == keys.BACKSPACE:
        if word_not_found:
            word_not_found = False
            continue
        if t9_engine.get_cur_completion_len() == 0:
            if len(line) == 0:
                continue
            line = line[:-1]
            recalculate_state()
        else:
            tmp = t9_engine.backspace()
            if not tmp:
                recalculate_state()
    elif key == keys.ENTER and word_not_found:
        new_word = input("\nnew word: ").strip()
        if len(new_word) != 0:
            t9_engine.add_word(new_word)
            with open("user_dict.txt", "a") as f:
                f.write(new_word + "\n")
            line += new_word + " "
            t9_engine.new_completion()
            word_not_found = False

