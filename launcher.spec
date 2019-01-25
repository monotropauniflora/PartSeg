# -*- mode: python -*-

block_cipher = None
import sys
import os
sys.setrecursionlimit(5000)
sys.path.append(os.path.dirname('__file__'))

import tifffile
# import plugins
import PartSeg.__main__
base_path = os.path.dirname(PartSeg.__main__.__file__)

num = tifffile.__version__.split(".")[0]

if num == '0':
    hiddenimports = ["tifffile._tifffile"]
else:
    hiddenimports = ["imagecodecs._imagecodecs"]

# print(["plugins." + x.name for x in plugins.get_plugins()])

a = Analysis(['launch_partseg.py'],
             # pathex=['C:\\Users\\Grzegorz\\Documents\\segmentation-gui\\PartSeg'],
             binaries=[],
             datas= [(os.path.join(base_path, x), y) for x,y in  [("static_files/icons/*", "PartSeg/static_files/icons"), ("static_files/initial_images/*", "PartSeg/static_files/initial_images"), ("static_files/colors.npz", "PartSeg/static_files/")]] +
                    [(os.path.join(base_path, "plugins/itk_snap_save/__init__.py"),"PartSeg/plugins/itk_snap_save")],
             hiddenimports=hiddenimports + ['numpy.core._dtype_ctypes'], # + ["plugins." + x.name for x in plugins.get_plugins()],
             hookspath=[],
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
          name='PartSeg_exec',
          debug=False,
          bootloader_ignore_signals=False,
          strip=False,
          upx=True,
          console=True )

coll = COLLECT(exe,
               a.binaries,
               a.zipfiles,
               a.datas,
               strip=False,
               upx=True,
               name='PartSeg')