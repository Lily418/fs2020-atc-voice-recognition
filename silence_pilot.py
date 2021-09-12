from pathlib import Path
import json
import re
import json

filter_rules = list(map(lambda r: re.compile(r), [ r"ATCCOM.AC.*"]))

p = Path(Path.home() / "AppData/Roaming/Microsoft Flight Simulator/Packages/Official/Steam/fs-base/en-US.locPak")
replaceMap= json.loads(open(Path(".") / "menu_item_replace.json",'r', encoding="utf8").read())

with open(p,'r', encoding="utf8") as f:
    locPak = json.loads(f.read())
    for item in locPak["LocalisationPackage"]["Strings"].items():
        for rule in filter_rules:
            if re.search(rule, item[0]):
                locPak["LocalisationPackage"]["Strings"][item[0]] = ""
                pass
        if replaceMap.get(item[0]) != None:
             locPak["LocalisationPackage"]["Strings"][item[0]] = replaceMap.get(item[0])


with open(p, 'w') as f:
    f.write(json.dumps(locPak, indent=4))