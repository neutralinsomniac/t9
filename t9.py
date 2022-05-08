#!/usr/bin/env python3

import time
import sys
import re
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
    CASE_MODE_NORMAL = 0
    CASE_MODE_CAPITALIZE = 1
    CASE_MODE_UPPER = 2

    T9 = {'.': 1, ',': 1, '!': 1, '?': 1,
          ':': 1, '-': 1, '_': 1, '\'': 1, '/': 1, '*': 1,
          '\\': 1, '(': 1, ')': 1, '<': 1, '>': 1,
          ';': 1, '[': 1, ']': 1,
          'a': 2, 'b': 2, 'c': 2,
          'd': 3, 'e': 3, 'f': 3,
          'g': 4, 'h': 4, 'i': 4,
          'j': 5, 'k': 5, 'l': 5,
          'm': 6, 'n': 6, 'o': 6,
          'p': 7, 'q': 7, 'r': 7, 's': 7,
          't': 8, 'u': 8, 'v': 8,
          'w': 9, 'x': 9, 'y': 9, 'z': 9,
          '0': 0, '1': 1, '2': 2, '3': 3,
          '4': 4, '5': 5, '6': 6, '7': 7,
          '8': 8, '9': 9}

    def __init__(self):
        self._lookup = {} # our dictionary
        self._cur = self._lookup # where we're sitting in the dictionary
        self._history = [] # breadcrumb pointers of the path we've taken through the dictionary
        self._completion_len = 0 # number of characters in the current completion state
        self._completion_choice = 0 # index into current 'words' array
        self._case_mode = self.CASE_MODE_CAPITALIZE
        self._doing_punctuation_stuff = False

    def add_word(self, word):
        cur = self._lookup
        # until I figure out a better way to handle this
        if "1" in word:
            return False
        for c in word:
            if c in "'":
                continue
            num = self.T9[c.lower()]
            if num not in cur:
                cur[num] = {}
            cur = cur[num]
        if "words" not in cur:
            cur["words"] = []
        if word not in cur["words"]:
            cur["words"].append(word)
            return True
        else:
            return False

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
        self._completion_len = max(self._completion_len - 1, 0)
        return self.get_completion()

    def get_completion(self):
        if self._completion_len == 0:
            return ""
        candidate = self._cur
        while candidate:
            if 'words' in candidate:
                word = candidate['words'][self._completion_choice % len(candidate['words'])]
                if self._case_mode == self.CASE_MODE_CAPITALIZE:
                    word = word.capitalize()
                elif self._case_mode == self.CASE_MODE_UPPER:
                    word = word.upper()
                return word
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

    def reset_completion_choice(self):
        self._completion_choice = 0

    def new_completion(self):
        self._cur = self._lookup
        self._history.clear()
        self._completion_choice = 0
        self._completion_len = 0

    def get_cur_completion_len(self):
        return len(self.get_completion())

    def get_num_engine_chars(self):
        return self._completion_len

    def set_case_mode(self, case_mode):
        self._case_mode = case_mode

    def cycle_case_mode(self):
        self._case_mode = (self._case_mode + 1) % 3

    def set_doing_punctuation_stuff(self, doing_punctuation_stuff):
        self._doing_punctuation_stuff = doing_punctuation_stuff

    def get_doing_punctuation_stuff(self):
        return self._doing_punctuation_stuff

def match_engine_to_word(t9_engine, word_to_match):
    # init the engine with the keys pressed for this word
    for c in word_to_match:
        if c in "'":
            continue
        if T9Engine.T9[c.lower()] == 1 and not t9_engine.get_doing_punctuation_stuff():
            t9_engine.new_completion()
            t9_engine.set_doing_punctuation_stuff(True)
        elif t9_engine.get_doing_punctuation_stuff() and T9Engine.T9[c.lower()] != 1:
            t9_engine.new_completion()
            t9_engine.set_doing_punctuation_stuff(False)
        try:
            t9_engine.add_digit(T9Engine.T9[c.lower()])
        except WordNotFoundException:
            t9_engine.new_completion()
            continue

def determine_capitalization(t9_engine, line):
    if len(line) == 0:
        t9_engine.set_case_mode(T9Engine.CASE_MODE_CAPITALIZE)
    for i, c in enumerate(line[::-1]):
        if c == " ":
            continue
        if c in ".!?":
            t9_engine.set_case_mode(T9Engine.CASE_MODE_CAPITALIZE)
        else:
            t9_engine.set_case_mode(T9Engine.CASE_MODE_NORMAL)
        break

def recalculate_state(t9_engine):
    global line

    # line is already empty
    if len(line) == 0:
        t9_engine.new_completion()
        t9_engine.set_case_mode(T9Engine.CASE_MODE_CAPITALIZE)
        return

    # determine the word we should try to match with the engine
    word_to_match = line.split(" ")[-1]
    if len(word_to_match) == 0:
        return

    m = re.split(r"([.!?]+)", word_to_match)
    m = list(filter(None, m))
    if len(m) != 0:
        word_to_match = m[-1]

    m = re.split(r"([a-zA-Z'1-9]+)", word_to_match)
    m = list(filter(None, m))
    word_to_match = m[-1]

    t9_engine.set_doing_punctuation_stuff(False)

    match_engine_to_word(t9_engine, word_to_match)

    if t9_engine.get_num_engine_chars() == 0:
        return

    # try to recover the completion choice that was made
    try_caseless = False
    try:
        while t9_engine.get_completion() != word_to_match:
            t9_engine.next_completion()
    except WordNotFoundException:
        t9_engine.reset_completion_choice()
        try_caseless = True
        pass

    # weird capitalization can make the above search fail, so let's try again ignoring case
    if try_caseless:
        try:
            while t9_engine.get_completion().casefold() != word_to_match.casefold():
                t9_engine.next_completion()
        except WordNotFoundException:
            # if we can't find the word at all, just bail
            t9_engine.new_completion()
            return

    # now that the word is loaded into the engine, remove it from the line
    line = line[:-1*t9_engine.get_cur_completion_len()]

    # should we capitalize the word?
    if not t9_engine.get_doing_punctuation_stuff():
        determine_capitalization(t9_engine, line)

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
engine_enabled = True
word_not_found = False

while True:
    # figure out how many of the completion characters are from input vs
    #  how many are from the engine attempting full completion
    completion = t9_engine.get_completion()
    num_keys_pressed = t9_engine.get_num_engine_chars()
    i = 0
    while i < num_keys_pressed:
        # apostrophes cause the number of chars output to not match the number of keys pressed
        if completion[i] in "'":
            num_keys_pressed += 1
        i += 1

    completion_left = completion[:num_keys_pressed]
    completion_right = completion[num_keys_pressed:]
    print(ERASE_LINE + "\r" + line + UNDERLINE_START + completion_left + UNDERLINE_END + completion_right +
            ("?" if word_not_found else ""), end='')

    key = getkey()

    if key == "Q":
        print("")
        break

    # for using a-z and period instead of numbers
    try:
        if not key.isdecimal():
            key = str(T9Engine.T9[key.lower()])
    except KeyError:
        pass

    if key in "123456789":
        if word_not_found:
            # don't allow input when the engine is stuck
            continue
        if key in "1":
            # punctuation
            if not t9_engine.get_doing_punctuation_stuff():
                t9_engine.set_doing_punctuation_stuff(True)
                line += t9_engine.get_completion()
                t9_engine.new_completion()
        else:
            # normal letter input
            if t9_engine.get_doing_punctuation_stuff():
                # if coming out of punctuation, insert the punctuation and
                #  start a new completion
                t9_engine.set_doing_punctuation_stuff(False)
                line += t9_engine.get_completion()
                t9_engine.new_completion()
        try:
            # feed the engine this digit
            t9_engine.add_digit(int(key))
        except WordNotFoundException:
            word_not_found = True
            pass
    elif key == keys.TILDE:
        # toggle engine state recalculation
        engine_enabled = not engine_enabled
        if engine_enabled:
            recalculate_state(t9_engine)
        else:
            line += t9_engine.get_completion()
            t9_engine.new_completion()
        word_not_found = False
    elif key == keys.CARET:
        # cycle case
        t9_engine.cycle_case_mode()
        word_not_found = False
    elif key == keys.TAB:
        # cycle next completion
        if word_not_found:
            # if the engine doesn't know the prediction, reset the choice back to the start
            t9_engine.reset_completion_choice()
            word_not_found = False
        else:
            try:
                t9_engine.next_completion()
            except WordNotFoundException:
                word_not_found = True
                pass
    elif key == "0" or key == keys.SPACE:
        # accept current completion and insert a space
        word_not_found = False
        completion = t9_engine.get_completion()
        line += completion + " "
        t9_engine.new_completion()
        if len(completion) != 0:
            if completion in ".!?":
                t9_engine.set_case_mode(T9Engine.CASE_MODE_CAPITALIZE)
            else:
                t9_engine.set_case_mode(T9Engine.CASE_MODE_NORMAL)
        t9_engine.set_doing_punctuation_stuff(False)
    elif key == keys.BACKSPACE:
        if word_not_found:
            # just clear the word not found state
            word_not_found = False
            continue
        if t9_engine.get_num_engine_chars() == 0:
            # engine is empty, so just remove a character from the line
            if len(line) == 0:
                continue
            line = line[:-1]
            # update engine with new state
            if engine_enabled: recalculate_state(t9_engine)
        else:
            tmp = t9_engine.backspace()
            # this handles the case where we backspaced out of one word, but
            #  ended up on top of another word (like with deleting punctuation
            #  or deleting parts of a word that isn't in the dictionary
            if not tmp:
                if engine_enabled: recalculate_state(t9_engine)
    elif key == keys.ENTER and word_not_found:
        # add new word to the dictionary (when the engine can't figure out what you want)
        new_word = input("\nnew word: ").strip()
        if len(new_word) != 0:
            if "1" in new_word or " " in new_word:
                print("'1' and ' ' are not supported characters in words")
                continue
            if t9_engine.add_word(new_word):
                # only add the word to the dictionary if it's actually new
                with open("user_dict.txt", "a") as f:
                    f.write(new_word + "\n")
            line += new_word
            t9_engine.new_completion()
            word_not_found = False
            if engine_enabled: recalculate_state(t9_engine)
    elif key == keys.ENTER:
        # accept the current completion (without outputting a space)
        line += t9_engine.get_completion()
        t9_engine.new_completion()
        t9_engine.set_case_mode(T9Engine.CASE_MODE_NORMAL)
        word_not_found = False
    elif key == "":
        # backspace the entire current completion, or back up one character
        if word_not_found:
            word_not_found = False
            continue
        if t9_engine.get_cur_completion_len() == 0:
            if len(line) == 0:
                continue
            line = line[:-1]
        else:
            t9_engine.new_completion()
            word_not_found = False
        if engine_enabled: recalculate_state(t9_engine)
