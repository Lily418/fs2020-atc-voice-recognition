# -*- mode: python ; coding: utf-8 -*-


block_cipher = None


a = Analysis(['index.py'],
             pathex=['C:\\Users\\lilyh\\Documents\\GitHub\\fs2020-atc-voice-recognition', 'C:\\Users\\lilyh\\Documents\\GitHub\\fs2020-atc-voice-recognition\\venv\\Lib\\site-packages'],
             binaries=[],
             datas=[(".\\vosk-model", ".\\vosk-model"), ('.\\venv\\Lib\\site-packages\\vosk', '.\\vosk'), (".\\menu_item_map.json", "."), (".\\menu_item_replace.json", ".")],
             hiddenimports=["altgraph","certifi","cffi","charset-normalizer","click","colorama","comtypes","filelock","future""huggingface-hub","idna","joblib","nltk","numpy","packaging","pefile","Pillow","pycparser","pynput","pyparsing","pytesseract","pywin32","pywin32-ctypes","pywinauto","PyYAML","regex","requests","sacremoses","scikit-learn","scipy","sentence-transformers","sentencepiece","six","sounddevice","threadpoolctl","tokenizers","torch","torchvision","tqdm","transformers","typing-extensions","vosk","urllib3"],
             hookspath=["hooks"],
             hooksconfig={},
             runtime_hooks=[],
             excludes=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher,
             noarchive=False)
pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)

exe = EXE(pyz,
          a.scripts, 
          [],
          exclude_binaries=True,
          name='index',
          debug=False,
          bootloader_ignore_signals=False,
          strip=False,
          upx=True,
          console=True,
          disable_windowed_traceback=False,
          target_arch=None,
          codesign_identity=None,
          entitlements_file=None )
coll = COLLECT(exe,
               a.binaries,
               a.zipfiles,
               a.datas, 
               strip=False,
               upx=True,
               upx_exclude=[],
               name='index')
