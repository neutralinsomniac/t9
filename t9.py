#!/usr/bin/env python3

import time
import sys
from getkey import getkey, keys

ERASE_LINE = '\x1b[2K'

# load dictionary
if len(sys.argv) != 2:
    print("usage: {} <dict.txt>".format(sys.argv[0]))
    sys.exit(1)

t9 = {'.': 1, '!': 1, '?': 1,
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

lookup = {}

def print_candidates(tree, n, ind=0):
    candidate = tree
    while candidate:
        if 'words' in candidate:
            print(ERASE_LINE + "\r" + candidate['words'][ind % len(candidate['words'])][:n] + " " + str(candidate['words']), end='')
            break
        for key in iter(candidate):
            if key != "words":
                candidate = candidate[key]
                break
    
def load_dict(filename):
    with open(sys.argv[1], "r") as dictionary:
        for word in dictionary.readlines():
            cur = lookup
            for c in word[:-1]:
                num = t9[c.lower()]
                if num not in cur:
                    cur[num] = {}
                cur = cur[num]
            if 'words' not in cur:
                cur['words'] = []
            cur['words'].append(word[:-1])

print("load...")
start = time.time()
load_dict(sys.argv[1])
print("loaded in {}s".format(time.time() - start))

cur = lookup
n = 0
history = []

exit = False
while exit == False:
    key = getkey()
    if key in '123456789':
        digit = int(key)
        if digit not in cur:
            continue
        n += 1
        print_candidates(cur[digit], n)
        history.append(cur)
        cur = cur[digit]
        ind = 0
        continue
    if key == keys.TAB:
        ind += 1
        print_candidates(cur, n, ind)
        continue
    elif key == '0' or key == keys.SPACE:
        cur = lookup
        n = 0
        history.clear()
        print("")
    elif key == keys.BACKSPACE:
        ind = 0
        if len(history) > 0:
            cur = history.pop()
            n -= 1
        else:
            cur = lookup
        if cur == lookup:
            print(ERASE_LINE + "\r", end='')
        else:
            print_candidates(cur, n)
        continue
    elif key == 'q':
        exit = True
        continue
