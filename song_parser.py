import py_midicsv as pm
import csv
from sys import argv
import os
TOO_LONG_A_GAP=3000
BASE_OCTAVE = {
    60: 'c',
    61: 'c#',
    62: 'd',
    63: 'd#',
    64: 'e',
    65: 'f',
    66: 'f#',
    67: 'g',
    68: 'g#',
    69: 'a',
    70: 'a#',
    71: 'b'
}

SCUM_KEYS = {
    'c': 'e',
    'c#': '4',
    'd': 'r',
    'd#': '5',
    'e': 't',
    'f': 'y',
    'f#': '7',
    'g': 'u',
    'g#': '8',
    'a': 'i',
    'a#': '9',
    'b': '0'
}

class MusicMan:
    def __init__(self, song: str):
        self.song = song
        self.song_data = list()

    # octave 0 is middle c
    # scum only support 3 octaves :( we move to highest/lowest and pretend its the right octave.
    @staticmethod
    def mangle_octaves(num_id):
        num_id = int(num_id)
        octave = 0
        if num_id not in BASE_OCTAVE:
            if 72 <= num_id <= 83:
                num_id -= 12
                octave = 1
            elif 84 <= num_id <= 95:
                num_id -= 24
                octave = 1
            elif 96 <= num_id <= 107:
                num_id -= 36
                octave = 1
            elif 108 <= num_id <= 119:
                num_id -= 48
                octave = 1
            elif 48 <= num_id <= 59:
                num_id += 12
                octave = -1
            elif 36 <= num_id <= 47:
                num_id += 24
                octave = -1
            elif 24 <= num_id <= 35:
                num_id += 36
                octave = -1
            elif 12 <= num_id <= 23:
                num_id += 48
                octave = -1
        return num_id, octave

    def convert_midi(self):
        # Load the MIDI file and parse it into CSV format
        csv_string = pm.midi_to_csv(open(self.song, 'rb'))
        with open(self.song + '.csv', '+w') as csvfile:
            csvfile.writelines(csv_string)

    def parse_csv(self):
        with open(self.song + '.csv', newline='') as csvfile:
            midi_data = csv.reader(csvfile, delimiter=',', quotechar='|')
            for row in midi_data:
                self.song_data.append(list(map(str.strip, row)))

    def parse_song(self):
        self.convert_midi()

    def split_instruments(self):
            new_song_data = dict()
            for midi_line in self.song_data:
                if midi_line[0] == 0:
                    continue
                if str(midi_line[0]) not in new_song_data:
                    new_song_data[str(midi_line[0])] = list()
                new_song_data[str(midi_line[0])].append(midi_line)
            return new_song_data

    def write_ahk_song(self, track):
        ahk_song = list()
        # Boilerplate
        ahk_song.append('#MaxThreadsPerHotkey 2 ; AHK Written by scum-musician https://github.com/scum-musician/scum-musician\n')
        ahk_song.append('#Singleinstance\n')
        ahk_song.append(f'{argv[2]}::\n')
        ahk_song.append('if (toggle := !toggle) {\n')
        ahk_song.append('Loop {\n')

        # Diff previous command timing to this in ms
        previous_timing = 0
        previous_octave = None
        last_note = None
        last_kp = None
        # Convert play speed to correct number type.
        try:
            play_speed = int(argv[4])
        except Exception:
            play_speed = float(argv[4])
        for c, tl in enumerate(track):
            if not tl[2][0:4] == 'Note':
                continue
            if not tl[4].isdigit():
                print(f'{tl[4]} is not a digit')
                continue
            timing = int(tl[1]) - abs(int(previous_timing))
            # Parameter which multiplies/divides the ms timestamp, can take a float or an int.
            adjusted_timing = timing * play_speed
            if abs(adjusted_timing) > abs(TOO_LONG_A_GAP):
                print(f'Timing at note {c} is {timing}')
                print(f'Adjusted Timing at note {c} is {adjusted_timing}')
                print(f'Previous timestamp: {previous_timing}')
                print(f'Current timestamp: {tl[1]}')

            if tl[2] == 'Note_off_c':
                key_press = 'up'
            elif tl[2] == 'Note_on_c':
                key_press = 'down'
            else:
                key_press = 'down'
            real_note, octave = self.mangle_octaves(tl[4])
            # We jump to the highest or lowest of the 3 octaves despite the real octave jump being higher.
            if previous_octave is not None:
                octave_jumps = max(previous_octave - octave, octave - previous_octave)
                if octave < previous_octave:
                    ahk_song.append('\nSend {LCtrl down}\nSend {LCtrl up}\n' * abs(octave_jumps))
                elif octave > previous_octave:
                    ahk_song.append('\nSend {LShift down}\nSend {LShift up}\n' * abs(octave_jumps))
                # If its a down press on the same note, Up press it first or we cant!
                if last_note == real_note and last_kp == 'down' and key_press != 'up':
                    ahk_song.append(f'\nSend {{{SCUM_KEYS[BASE_OCTAVE[real_note]]} up}}\n')
                ahk_song.append(f'\nSend {{{SCUM_KEYS[BASE_OCTAVE[real_note]]} {key_press}}}\nSleep {adjusted_timing}\n')
                last_note = real_note
            last_kp = key_press
            previous_octave = octave
            previous_timing = tl[1]
        ahk_song.append('if (!toggle) {\n')
        ahk_song.append('ExitApp\n')
        ahk_song.append('}\n')
        ahk_song.append('}\n')
        ahk_song.append('} else {\n')
        ahk_song.append('ExitApp\n')
        ahk_song.append('} ; AHK Written by scum-musician https://github.com/scum-musician/scum-musician\n')
        return ahk_song


if __name__ == '__main__':
    print('Usage examples:')
    print('python3 [midifile] [hotkey] [instrumentstart] [speed_multiplier]')
    print('python3 song.midi F2 3 1')
    print('If your AHK is not produced, Lower the [instrumentstart] number by 1')
    if len(argv) < 4:
        exit(0)
    mm = MusicMan(song=argv[1])
    song = argv[1]
    if not os.path.isfile(song + '.csv'):
        mm.convert_midi()
    mm.parse_csv()
    nsd = mm.split_instruments()
    for instrument, track in nsd.items():
        if int(instrument) < int(argv[3]):
            continue
        ahk_song = mm.write_ahk_song(track)
        with open(f'instrument_{song}_{instrument}.ahk', 'w') as instrument_ahk:
            instrument_ahk.writelines(ahk_song)
    print("Finished!")
