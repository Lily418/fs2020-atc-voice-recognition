from PyInstaller.utils.hooks import copy_metadata
from PyInstaller.utils.hooks import collect_all

copy_metadata('transformers')
datas, binaries, hiddenimports = collect_all('transformers')
