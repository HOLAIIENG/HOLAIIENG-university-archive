import os,ctypes,traceback
p = os.path.normpath(r'C:\Users\jessi\Desktop\HOLAIIENG-university-archive\.venv\Lib\site-packages\PyQt5')
paths = [os.path.join(p,'QtWidgets.pyd'), os.path.join(p,'Qt5Widgets.dll')]
for pp in paths:
    print('\nTrying to load:', pp)
    print('exists:', os.path.exists(pp))
    try:
        ctypes.WinDLL(pp)
        print('Loaded OK')
    except Exception:
        traceback.print_exc()

print('\nAlso try to inspect dependent DLL names by using pefile if available (optional)')
try:
    import pefile
    for pp in paths:
        if os.path.exists(pp):
            pe = pefile.PE(pp)
            print(pp, '-> DLL dependencies:')
            for entry in pe.DIRECTORY_ENTRY_IMPORT:
                print('  ', entry.dll.decode())
except Exception as e:
    print('pefile not available or failed:', e)
print('done')

