A sane T9 engine.

Features:
- contractions (just type the word like you would if the apostrophe didn't exist. no need to hit '1')
- re-completions on backspace
- persistant custom dictionary

Keys:
- 1-9: normal T9 input
- a-z, punctuation: alternate input. maps to one of the 1-9 keys.
- Tab: next completion
- 0 or space: accept completion and insert a space
- Backspace: delete character
- Enter: when '?' is showing (indicating an unknown word), hit enter to add a custom word to the dictionary

Quickstart:
```
git clone https://github.com/neutralinsomniac/t9.git
cd t9
python3 -m venv .
source bin/activate
pip install -r requirements.txt
./t9.py google-10000-english-usa.txt
```
