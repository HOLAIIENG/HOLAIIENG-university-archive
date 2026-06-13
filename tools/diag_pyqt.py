import os
import ctypes
import traceback

p = os.path.join(os.path.dirname(__file__), '..', '.venv', 'Lib', 'site-packages', 'PyQt5')
p = os.path.normpath(p)
print('PyQt5 dir:', p)
core = os.path.join(p, 'Qt5Core.dll')
widgets = os.path.join(p, 'Qt5Widgets.dll')
print('Qt5Core exists:', os.path.exists(core))
print('Qt5Widgets exists:', os.path.exists(widgets))

print('\nTry ctypes.WinDLL on Qt5Core.dll')
try:
    ctypes.WinDLL(core)
    print('ctypes loaded Qt5Core OK')
except Exception:
    traceback.print_exc()

print('\nTry importing PyQt5.QtWidgets directly')
try:
    from PyQt5 import QtWidgets
    print('Imported PyQt5.QtWidgets OK')
except Exception:
    traceback.print_exc()

print('\nTry prepending PyQt5 dir to PATH and import again')
import os
os.environ['PATH'] = p + os.pathsep + os.environ.get('PATH','')
try:
    from PyQt5 import QtWidgets
    print('Imported after PATH prepend OK')
except Exception:
    traceback.print_exc()

print('\nEnvironment PATH startswith PyQt5 dir? ', os.environ['PATH'].startswith(p))
print('Done')

