import pyautogui
import time

pyautogui.PAUSE = 1

pyautogui.hotkey("win")                 # clica em windows
pyautogui.write('cmd')                  # digita o cmd no campo
pyautogui.hotkey("enter")               # aperta o enter
time.sleep(1)
pyautogui.write('python')               # digita python na janela do comando
pyautogui.hotkey("enter")               # aperta o enter
time.sleep(1)
pyautogui.write('from mouseinfo import mouseInfo') # digita o mouseInfo para carregar a biblioteca pro python
pyautogui.hotkey("enter")               # aperta o enter
time.sleep(1)
pyautogui.write('mouseInfo()')          # digita o mouseInfo para carregar a biblioteca pro python
pyautogui.hotkey("enter")               # aperta o enter
