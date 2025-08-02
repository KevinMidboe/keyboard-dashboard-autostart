#!/usr/bin/python3
import struct, os, sys, subprocess, threading
from time import sleep, time
from evdev import InputDevice, categorize, ecodes, list_devices
from functools import partial

USER='kevin'
chromeBin = '/usr/bin/chromium-browser'
BOOKMARK_DIR = f'/home/{USER}/.config/chromium/Default'

def findKeyboard():
  devices = [InputDevice(path) for path in list_devices()]
  for device in devices:
    if 'keyboard' in device.name.lower() or 'kbd' in device.name.lower():
      return device

  raise Exception('Keyboard device not found. You may need to run as root.')

def getBookmarks():
  cmd = f"cat {BOOKMARK_DIR}/Bookmarks | jq '.roots.bookmark_bar.children[0].children[] | .url' | tr '\\n' ' '"

  result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=isinstance(cmd, str), text=True, check=True)
  return result.stdout.strip()

def programRunning(cmd, onlyPrefix=False):
  if onlyPrefix:
    cmd = cmd.split(' ')[0]

  try:
    subprocess.run(["pgrep", "-f", cmd], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
    return True
  except subprocess.CalledProcessError:
    return False

def buildUserCommand(cmd):
  userSpaceCmd = f'su - {USER} -c'
  userDisplayCmd = 'export DISPLAY=:0; '
  cmdList = userSpaceCmd.split(' ')
  cmdList.append(userDisplayCmd + cmd)
  return cmdList

def openBrowser():
  bookmarks = getBookmarks()
  browserCmd = chromeBin + ' \
  --no-first-run \
  --disable \
  --hide-crash-restore-bubble \
  --disable-translate \
  --disable-infobars \
  --disable-suggestions-service \
  --disable-save-password-bubble \
  --kiosk ' \
  + bookmarks

  if programRunning(browserCmd, True):
    print('browser already running, exiting')
    return

  print('launching browser')
  runUnclutter()
  cmd = buildUserCommand(browserCmd)
  subprocess.Popen(cmd)

def openTerminal(cmd, windowHeight=None, windowY=None):
  if programRunning(cmd):
    print('terminal already running w/ this command, exiting')
    return

  print('launching terminal w/ command:', cmd)
  cmd = f'lxterminal -e "{cmd}"'

  cmd = buildUserCommand(cmd)
  subprocess.Popen(cmd)

def runUnclutter():
  program = 'unclutter'
  if programRunning(program):
    print(f"{program} already running")
    return

  print(f"starting {program}")
  cmd = buildUserCommand(f'{program} &')
  subprocess.run(cmd)

def startup():
  timeout = 1
  print("waiting {} seconds, then launching chrome".format(timeout))
  sleep(timeout)
  openBrowser()

def listenForInput():
  print("listening for keyboard input")

  try:
    dev = findKeyboard()
    print(f'Listening to: {dev.name} ({dev.path})')

    for event in dev.read_loop():
      if event.type != ecodes.EV_KEY:
        continue

      key_event = categorize(event)
      if key_event.keystate != key_event.key_down:
        continue

      print(f'Keycode: {key_event.keycode}')
      if key_event.keycode not in KEY_EVENT_PROGRAM_MAP:
        continue

      KEY_EVENT_PROGRAM_MAP[key_event.keycode]()

  except PermissionError:
    print('Permission denied. Try running with sudo or check device permissions.')
  except Exception as e:
    print(f'Error: {e}')

KEY_EVENT_PROGRAM_MAP = {
  'KEY_F16': openBrowser,
  'KEY_F17': partial(openTerminal, 'watch -n 1 "sensors | grep temp1"')
}

def printHelp():
  print("Available key bindings:\n")
  for key, func in KEY_EVENT_PROGRAM_MAP.items():
    key = key.replace('KEY_', '')

    if isinstance(func, partial):
      func_name = func.func.__name__
      args = ", ".join(repr(arg) for arg in func.args)
      print(f"{key}: {func_name}({args})")
    else:
      func_name = func.__name__ if hasattr(func, '__name__') else str(func)
      print(f"{key}: {func_name}()")

def main():
  backgroundStartupThread = threading.Thread(target=startup)
  backgroundStartupThread.start()

  listenForInput()

if __name__ == '__main__':
    if '-h' in sys.argv or '--help' in sys.argv:
      printHelp()
      sys.exit(0)
    else:
      main()

