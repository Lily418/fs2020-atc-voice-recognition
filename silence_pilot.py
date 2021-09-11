from pathlib import Path
import json
import re

filter_rules = list(map(lambda r: re.compile(r), [ r"ATCCOM.AC.*"]))

p = Path(Path.home() / "AppData/Roaming/Microsoft Flight Simulator/Packages/Official/Steam/fs-base/en-US.locPak")

with open(p,'r', encoding="utf8") as f:
    locPak = json.loads(f.read())
    for item in locPak["LocalisationPackage"]["Strings"].items():
        for rule in filter_rules:
            if re.search(rule, item[0]):
                locPak["LocalisationPackage"]["Strings"][item[0]] = ""
        
        # if locPak["LocalisationPackage"]["Strings"][item[0]] != "" and re.search(re.compile(r"ATCCOM"), item[0]):
        #     locPak["LocalisationPackage"]["Strings"][item[0]] = "locPack Code" + item[0]

with open(p, 'w') as f:
    f.write(json.dumps(locPak, indent=4))