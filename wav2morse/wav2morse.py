from os.path import abspath
import wave
import numpy as np
import itertools
import re

def get_morse_key():
    morse_key = {
        "A": ".-",
        "B": "-...",
        "C": "-.-.",
        "D": "-..",
        "E": ".",
        "F": "..-.",
        "G": "--.",
        "H": "....",
        "I": "..",
        "J": ".---",
        "K": "-.-",
        "L": ".-..",
        "M": "--",
        "N": "-.",
        "O": "---",
        "P": ".--.",
        "Q": "--.-",
        "R": ".-.",
        "S": "...",
        "T": "-",
        "U": "..-",
        "V": "...-",
        "W": ".--",
        "X": "-..-",
        "Y": "-.--",
        "Z": "--..",
        "1": ".----",
        "2": "..---",
        "3": "...--",
        "4": "....-",
        "5": ".....",
        "6": "-....",
        "7": "--...",
        "8": "---..",
        "9": "----.",
        "0": "-----"
    }
    return morse_key

def morse_to_character(morse):
    morse_key = get_morse_key()
    for key, value in morse_key.items():
        if value == morse:
            return key

def split_square_wave(square_wave):
    result = []
    current_value = square_wave[0]
    start_index = 0

    for i in range(1, len(square_wave)):
        if square_wave[i] != current_value:
            result.append(square_wave[start_index:i])
            current_value = square_wave[i]
            start_index = i

    # Append the last segment
    result.append(square_wave[start_index:])

    return result

def filter_alphanumeric(text):
    return re.sub(r'\W+', '', text)

def fix_x_crossing(split_wave, zeroth_term, first_term, repetitions=2):
    for i in range(repetitions):
        if len(split_wave[0]) < 10:
            split_wave[1] = list(itertools.chain(split_wave[0], split_wave[1]))
            split_wave = split_wave[1:]
            zeroth_term = first_term
        fixed_wave = []
        skips_queued = 0
        for i in range(len(split_wave)-2):
            if skips_queued > 0:
                skips_queued -= 1
                continue
            if len(split_wave[i+1]) < 10:
                new_array = list(itertools.chain(split_wave[i], split_wave[i+1], split_wave[i+2]))
                fixed_wave.append(new_array)
                skips_queued = 2
            else:
                fixed_wave.append(split_wave[i])
        split_wave = fixed_wave
    return fixed_wave, zeroth_term

def decode_morse(frames):
    frames = np.frombuffer(frames, dtype=np.int16)
    if frames[0] == 0:
        zeroth_term = 0
    else:
        zeroth_term = 1
    if frames[1] == 0:
        first_term = 0
    else:
        first_term = 1
    square_wave = np.where(frames != 0, 1, 0)
    split_wave = split_square_wave(square_wave)
    fixed_wave, zeroth_term = fix_x_crossing(split_wave, zeroth_term, first_term)
    unit_length = 99999999
    lengths = []
    for wave in fixed_wave:
        lengths.append(len(wave))
    unit_length = min(lengths)
    divided_lengths = []
    for length in lengths:
        divided_lengths.append(round(length/unit_length))
    if zeroth_term == 0:
        divided_lengths = divided_lengths[1:]
    words = []
    sublist = []
    for i in divided_lengths:
        if i == 8:
            if sublist:
                words.append(sublist)
            sublist = []
        else:
            sublist.append(i)
    
    if sublist:
        words.append(sublist)
    new_words = []
    for word in words:
        new_word = ""
        for j in range(len(word)):
            i = word[j]
            if i == 4:
                new_word += " "
            elif j%2 == 1:
                continue
            elif i == 1:
                new_word += "."
            elif i == 3:
                new_word += "-"
        new_words.append(new_word)
    final_words = []
    for word in new_words:
        final_word = ""
        for char in word.split(" "):
            final_word += morse_to_character(char)
        final_words.append(final_word)
    message = ""
    morse_message = ""
    for word in new_words:
        morse_message += word + " / "
    for word in final_words:
        message += word + " "
    return morse_message[0:-3], message.rstrip()
    


def wav2morse(input_file_path, morse_output=False, lowercase=False):

    input_file_path = abspath(input_file_path)
    input_wave = wave.open(input_file_path, "rb")

    # Read the frames of the wave file
    frames = input_wave.readframes(input_wave.getnframes())

    morse_message, message = decode_morse(frames)
    
    if morse_output:
        return morse_message
    else:
        if lowercase:
            return message.lower()
        else:
            return message
        
def morse2text(morse, lowercase=False):
    words = morse.split(" / ")
    final_string = ""
    for word in words:
        characters = word.split(" ")
        for char in characters:
            final_string += morse_to_character(char)
        final_string += " "
    final_string = final_string.rstrip()
    if lowercase:
        final_string = final_string.lower()
    return final_string

def text2morse(text):
    text = filter_alphanumeric(text)
    text = text.upper()
    morse_key = get_morse_key()
    words = text.split(" ")
    for i in range(len(words)):
        word = words[i]
        morse_word = ""
        for char in word:
            morse_word += morse_key[char] + " "
        words[i] = morse_word
    final_string = ""
    for word in words:
        final_string += word + "/ "
    return final_string[0:-2]

if __name__ == "__main__":
    print("This script is not meant to be run directly. Please use the morse-tools command line utility instead.")