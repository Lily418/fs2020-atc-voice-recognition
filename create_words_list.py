from pathlib import Path
import json
import re


p = Path(Path(".") / "original.locPak")
words_list = Path(Path(".") / "pilot_words.txt")

filter_rules = list(map(lambda r: re.compile(r), [ r"ATCCOM.AC.*.text"]))

variable_rule = r"\{[a-zA-Z_]+\}|[^\w\s]"

with open(p,'r', encoding="utf8") as f:
    with open(words_list, "w") as wl:
        locPak = json.loads(f.read())
        for item in locPak["LocalisationPackage"]["Strings"].items():
            for rule in filter_rules:
                if re.search(rule, item[0]):
                    wl.write(re.sub(variable_rule, '', item[1]).lower().strip() + " ")