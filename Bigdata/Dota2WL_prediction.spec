# -*- mode: python -*-

block_cipher = None


a = Analysis(['Dota2WL_prediction.py'],
             pathex=['D:\\py\\Lib\\site-packages\\PyQt5\\Qt\\bin', 'C:\\Users\\dell\\Bigdata'],
             binaries=[],
             datas=[],
             hiddenimports=['sklearn.neighbors.typedefs', 'sklearn.linear_model'],
             hookspath=[],
             runtime_hooks=[],
             excludes=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher)
pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)
exe = EXE(pyz,
          a.scripts,
          a.binaries,
          a.zipfiles,
          a.datas,
          name='Dota2WL_prediction',
          debug=False,
          strip=False,
          upx=True,
          runtime_tmpdir=None,
          console=False )
