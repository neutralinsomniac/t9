#!/usr/bin/env python3

import time
import sys

# load dictionary
if len(sys.argv) != 2:
    print("usage: {} <dict.txt>".format(sys.argv[0]))
    sys.exit(1)

t9 = {'\'': 1,
      'a': 2, 'b': 2, 'c': 2,
      'd': 3, 'e': 3, 'f': 3,
      'g': 4, 'h': 4, 'i': 4,
      'j': 5, 'k': 5, 'l': 5,
      'm': 6, 'n': 6, 'o': 6,
      'p': 7, 'q': 7, 'r': 7, 's': 7,
      't': 8, 'u': 8, 'v': 8,
      'w': 9, 'x': 9, 'y': 9, 'z': 9}

lookup = {}

def print_candidates(tree, n):
    candidate = cur[int(c)]
    while candidate:
        if 'words' in candidate:
            print(candidate['words'][0][:n] + " " + str(candidate['words']))
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


for line in sys.stdin:
    cur = lookup
    n = 0
    for c in line[:-1]:
        n += 1
        if int(c) in cur:
            if 'words' in cur[int(c)]:
                print(cur[int(c)]['words'][0][:n] + " " + str(cur[int(c)]['words']))
            else:
                print_candidates(cur[int(c)], n)
        else:
            print("NOPE")
            break
        cur = cur[int(c)]
