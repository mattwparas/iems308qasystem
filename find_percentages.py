import re
import pandas as pd

def find_percentages(sentence):
    exp1 = f"\d+(?:\.\d+)?(?:%| percent?)"
    exp2 = f"\d+(?:\.\d+)?(?:%| percentage points?)"
    # super ugly regex cause idk how to make them better
    exp3 = f"(?:(?:one|two|three|four|five|six|seven|eight|nine)| \
    (?:eleven|twelve|thirteen|fourteen|fifteen|sixteen|seventeen|eighteen|nineteen)| \
    (?:twenty|thirty|forty|fifty|sixty|seventy|eighty|ninety)|(?: \
    (?:twenty|thirty|forty|fifty|sixty|seventy|eighty|ninety)-(?:one|two|three|four|five|six|seven|eight|nine))) \
    percent?"
    # super ugly regex round 2 cause idk how to make them better
    exp4 = f"(?:(?:one|two|three|four|five|six|seven|eight|nine)| \
    (?:eleven|twelve|thirteen|fourteen|fifteen|sixteen|seventeen|eighteen|nineteen)| \
    (?:twenty|thirty|forty|fifty|sixty|seventy|eighty|ninety)|(?: \
    (?:twenty|thirty|forty|fifty|sixty|seventy|eighty|ninety)-(?:one|two|three|four|five|six|seven|eight|nine))) \
    percentage points?"
    exp5 = f"point (?:(?:one|two|three|four|five|six|seven|eight|nine)| \
    (?:eleven|twelve|thirteen|fourteen|fifteen|sixteen|seventeen|eighteen|nineteen)| \
    (?:twenty|thirty|forty|fifty|sixty|seventy|eighty|ninety)|(?: \
    (?:twenty|thirty|forty|fifty|sixty|seventy|eighty|ninety)-(?:one|two|three|four|five|six|seven|eight|nine))) \
    percent?"
    exp6 = f"point (?:(?:one|two|three|four|five|six|seven|eight|nine)| \
    (?:eleven|twelve|thirteen|fourteen|fifteen|sixteen|seventeen|eighteen|nineteen)| \
    (?:twenty|thirty|forty|fifty|sixty|seventy|eighty|ninety)|(?: \
    (?:twenty|thirty|forty|fifty|sixty|seventy|eighty|ninety)-(?:one|two|three|four|five|six|seven|eight|nine))) \
    percentage points?"
    exp7 = f"point \d+(?:\.\d+)?(?:%| percent?)"
    exp8 = f"point \d+(?:\.\d+)?(?:%| percentage points?)"

    matches = []
    percents1 = re.findall(exp1, sentence)
    percents2 = re.findall(exp2, sentence)
    percents3 = re.findall(exp3, sentence)
    percents4 = re.findall(exp4, sentence)
    percents5 = re.findall(exp5, sentence)
    percents6 = re.findall(exp6, sentence)
    percents7 = re.findall(exp7, sentence)
    percents8 = re.findall(exp8, sentence)
    
    percents = list(set(percents1 + percents2 + percents3 + percents4 + percents5 + percents6 + percents7 + percents8))
    
    if percents:
        for percentage in percents:
            matches.append(percentage)
                
    return matches