A sane T9 engine.

![t9demo](https://pintobyte.com/tmp/t9_demo_light.gif)

Features:
- contractions (just type the word like you would if the apostrophe didn't exist. no need to hit '1')
- re-completions on backspace
- auto capitalization/custom capitalization
- persistent custom dictionary

Keys:
- 1-9: normal T9 input (1 is punctuation, 2-9 is a-z)
- a-z, punctuation: alternate input for QWERTY keyboards. maps to one of the 1-9 keys.
- Tab: next completion
- 0 or space: accept completion and insert a space
- Backspace: delete character
- Enter: when '?' is showing (indicating an unknown word): add a custom word to
  the dictionary. Otherwise, accept the current completion without adding a space
- ^: cycle capitalization mode
- ctrl-w: backspace entire current word
- ~: toggle T9 engine on and off
- ctrl-c: copy current line to clipboard
- ctrl-u: clear entire line

Quickstart:
```
git clone https://github.com/neutralinsomniac/t9.git
cd t9
python3 -m venv .
source bin/activate
pip install -r requirements.txt
./t9.py google-10000-english-usa.txt
```
