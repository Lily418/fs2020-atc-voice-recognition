from pathlib import Path
p = Path('.') / "atc-archive"
print([x for x in p.iterdir() if x.is_dir()])