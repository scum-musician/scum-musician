## Scum Musician
This is a midifile to CSV converter that writes an AHK script to play scum instruments.

I wanted to use a reliable widely used key input application to play the notes.

I spent roughly 6 hours writing it and a few more testing it. However it relies heavily on the other FOSS software it utilises and more credit is owed to those authors then myself.

*Shoutout to*
- py_midicsv
- All the song authors and website owner from http://bmp.sqnya.se/songs.php
- The Python language contributors
- The profile picture author: Michael Gustafsson

The quality of the output is entirely dependant on the midi file used. I have found the best working songs marked SOLO on http://bmp.sqnya.se/songs.php.
However you could use the multiple AHK songs generated from > duets and play with your buddies if you all started at the right time and had good fps and similar lag. 

Scum only has 3 octaves and no octave modifier, FPS/Lag all have an effect on the ability for AHK to smash the octave change keys mid song.

##### If you want to spread this around, Link to this github page. Do not post the files uncredited. 

### Installation and setup on windows
- Install Python 3.7

https://www.python.org/downloads/

- Install the requirements.txt packages from a command prompt

`python -m pip install py_midicsv`

### Installation and setup on Linux
- Install the requirements.txt packages from a command prompt

`pip3 install -r requirements.txt` 

### Usage
If using windows you might have to type python instead of python3.
Multiple instruments will create multiple AHK files.
If no AHK is generated lower the "instrument start" number by 1.
```
python3 [midifile] [hotkey] [instrumentstart] [speed_multiplier]'
python3 song.midi F2 3 1'
```
