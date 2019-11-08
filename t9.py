#!/usr/bin/env python3

import time
import sys
from getkey import getkey, keys

ERASE_LINE = '\x1b[2K'

# load dictionary
if len(sys.argv) != 2:
    print("usage: {} <dict.txt>".format(sys.argv[0]))
    sys.exit(1)

class T9Engine():
    T9 = {'.': 1, '!': 1, '?': 1,
          ':': 1, '-': 1, "'": 1,
          '(': 1, ')': 1, ';': 1,
          'a': 2, 'b': 2, 'c': 2,
          'd': 3, 'e': 3, 'f': 3,
          'g': 4, 'h': 4, 'i': 4,
          'j': 5, 'k': 5, 'l': 5,
          'm': 6, 'n': 6, 'o': 6,
          'p': 7, 'q': 7, 'r': 7, 's': 7,
          't': 8, 'u': 8, 'v': 8,
          'w': 9, 'x': 9, 'y': 9, 'z': 9}

    def __init__(self):
        self._lookup = {}
        self._cur = self._lookup
        self._history = []
        self._n = 0
        self._ind = 0

    def load_dict(self, filename):
        with open(filename, 'r') as dictionary:
            for word in dictionary.readlines():
                cur = self._lookup
                for c in word[:-1]:
                    num = self.T9[c.lower()]
                    if num not in cur:
                        cur[num] = {}
                    cur = cur[num]
                if 'words' not in cur:
                    cur['words'] = []
                cur['words'].append(word[:-1])

    def add_digit(self, digit):
        if digit not in self._cur:
            return False
        self._n += 1
        self._history.append(self._cur)
        self._cur = self._cur[digit]
        self._ind = 0
        return self.get_completion()

    def backspace(self):
        self._ind = 0
        if len(self._history) > 0:
            self._cur = self._history.pop()
            self._n -= 1
            return self.get_completion()
        else:
            self._cur = self._lookup
            return False

    def get_completion(self):
        candidate = self._cur
        while candidate:
            if 'words' in candidate:
                return candidate['words'][self._ind % len(candidate['words'])][:self._n]
            for key in iter(candidate):
                if key != "words":
                    candidate = candidate[key]
                    break

    def next_completion(self):
        self._ind += 1
        return self.get_completion()

    def new_completion(self):
        self._cur = self._lookup
        self._history.clear()
        self._ind = 0
        self._n = 0

    def get_cur_completion_len(self):
        return self._n
    

t9_engine = T9Engine()

print("load...")
start = time.time()
t9_engine.load_dict(sys.argv[1])
print("loaded in {}s".format(time.time() - start))

line = ''
cur_word = ''

exit = False
while exit == False:
    key = getkey()
    if key in '123456789':
        tmp = t9_engine.add_digit(int(key))
        if tmp:
            cur_word = tmp
    elif key == keys.TAB:
        cur_word = t9_engine.next_completion()
    elif key == '0' or key == keys.SPACE:
        line += cur_word + ' '
        cur_word = ''
        t9_engine.new_completion()
    elif key == keys.BACKSPACE:
        if t9_engine.get_cur_completion_len() == 0:
            if len(line) == 0:
                continue
            line = line[:-1]
            words = line.split(' ')
            cur_word = words[-1]
            if len(cur_word) != 0:
                line = line[:-1*len(cur_word)]
            for c in cur_word:
                t9_engine.add_digit(T9Engine.T9[c])
        else:
            tmp = t9_engine.backspace()
            if tmp:
                cur_word = tmp
            else:
                cur_word = ''
    elif key == 'q':
        exit = True
    print(ERASE_LINE + "\r" + line + cur_word, end='')
