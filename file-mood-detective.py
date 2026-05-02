import argparse
from pathlib import Path

def binary(file):
    file = Path(file)

    with open(file, "rb") as f:
        data = f.read()

    score = sum(data)
    div = len(data) * 256 / 2

    delta = score / div

    qmood = ""

    if delta < 0.1:
        qmood = "the_void_"          # Almost entirely null bytes or low control codes
    elif delta < 0.2:
        qmood = "eerie_"         # Sparse, rhythmic, mostly empty
    elif delta < 0.3:
        qmood = "somber_"        # Low-density, very "quiet" data
    elif delta < 0.4:
        qmood = "minimal_"       # Clean, simple, lots of whitespace
    elif delta < 0.5:
        qmood = "low_cortisol_"       # Typical of sparse text or lists
    elif delta < 0.6:
        qmood = "calm_"          # Standard low-ASCII text range
    elif delta < 0.7:
        qmood = "steady_"        # Balanced prose
    elif delta < 0.8:
        qmood = "active_"        # Denser text, more varied characters
    elif delta < 0.9:
        qmood = "bright_"        # Upper-end of standard ASCII/text
    elif delta < 1.0:
        qmood = "vibrant_"       # Transitioning into complex character sets
    elif delta < 1.1:
        qmood = "complex_"       # Mixture of standard and special characters
    elif delta < 1.2:
        qmood = "whimsical_"     # Occasional high-byte symbols/emojis
    elif delta < 1.3:
        qmood = "high_cortisol_"      # High variety of byte values
    elif delta < 1.4:
        qmood = "intense_"       # Heavy use of extended ASCII or encoded data
    elif delta < 1.5:
        qmood = "rough_"      # Sharp, high-value byte patterns
    elif delta < 1.6:
        qmood = "electric_"      # Fast-changing, high-energy bytes
    elif delta < 1.7:
        qmood = "overloaded_"    # Very dense, possibly binary or compressed
    elif delta < 1.8:
        qmood = "adhd_"         # Near-constant high-value signals
    elif delta < 1.9:
        qmood = "chaotic_"       # Extreme density
    elif delta < 2.0:
        qmood = "absolute_end_"      # Maximum saturation (nearly all bytes are 255)

    file.rename(f"{qmood}{file.name}")

    print(f"This file is {qmood.capitalize().replace("_", " ")}")

def text_based(file):
    print("This hasn't been implemented yet")
    print("I might add this (if i don't get distracted by another project)")
    print("Feel free to add it yourself, some of my code is already present")
    #values to fine-tune
    # CAPS_THRESHOLD = 0.6
    # QUESTION_MIT_MULT = 0.5
    # LENGHT_THRESHOLD = 20

    # def determine_energy(data:str) -> list:
    #     """returns exclamation (!), thinking (...), question (?), CAPS / no caps"""
    #     totallines = len(data.splitlines())
    #     exclamation = data.count("!") / totallines
    #     question = data.count("?") / totallines
    #     thinking = data.count("...") / totallines

    #     caps = sum(1 for char in data if char.isupper())
    #     nocaps = sum(1 for char in data if char.islower())
        
    #     # Safety check to avoid division by zero
    #     ratio = caps / nocaps if nocaps > 0 else float(caps)

    #     return [exclamation, thinking, question, ratio]

    # def determine_flow(data:str) -> list:
    #     """returns min, average, max"""
    #     lines = data.splitlines()
    #     lengths = []
    #     for l in lines:
    #         lengths.append(len(l))
    #     average = sum(lengths) / len(lengths)
    #     return [min(lengths), average, max(lengths)]

    # 
    # with open(file, "r") as f:
    #     data = f.read()
    
    # energy = determine_energy(data)

    # if energy[3] > CAPS_THRESHOLD:
    #     question_mitigation = QUESTION_MIT_MULT
    # else:
    #     question_mitigation = 0     
    
    # energy[2] *= question_mitigation

    # tenergy = (energy[1] + energy[0] - energy[2]) / sum(energy[:3])

    # flow = determine_flow(data)

    # if flow[]

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("file")
    parser.add_argument("-b", help="Binary mode", action="store_true")
    parser.add_argument("-t", help="Text mode", action="store_true")
    args = parser.parse_args()
    if args.b:
        binary(args.file)
    if args.t:
        text_based(args.file)