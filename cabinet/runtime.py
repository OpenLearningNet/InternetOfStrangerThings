from machine import Timer, Pin
import network
import time
import os

timer = Timer(-1)

SETTINGS_FILENAME = 'settings.txt'
SLEEP_TIME_MS = 10
SETUP_HTML = """<!DOCTYPE html>
<html>
    <head> <title>Device Setup</title> </head>
    <body> <h1>Device Setup</h1>
      <div>%s</div>
      <form method="POST" action="#">
        ESSID: <input type="text" name="essid"><br/>
        Password: <input type="text" name="password"><br/>
        <input type="submit" value="Save">
      </form>
    </body>
</html>
"""
SETUP_TIME_S = 10

def wifi_connect(essid, password):
  wlan = network.WLAN(network.STA_IF)
  wlan.active(True)
  if not wlan.isconnected():
    print('connecting to network...')
    wlan.connect(essid, password)
    while not wlan.isconnected():
      time.sleep_ms(100)
      print('.', end='')
  print(' connected.')
  print('network config:', wlan.ifconfig())
  return wlan

def wifi_setup():
  # create a temporary access point for setup
  access_point = network.WLAN(network.AP_IF)
  access_point.config(essid='Cabinet Setup', authmode=0)
  run_setup()
  access_point.active(False)

def run_setup():
  # start listening for connections
  import socket
  addr = socket.getaddrinfo('0.0.0.0', 80)[0][-1]
  s = socket.socket()
  s.bind(addr)
  s.listen(1)
  print('listening on', addr)
  
  if SETTINGS_FILENAME in os.listdir():
    print('existing settings found. timing out in %s seconds' % SETUP_TIME_S)
    s.settimeout(SETUP_TIME_S)
  
  is_set_up = False
  confirmation = ''
  while not is_set_up:
    try:
      cl, addr = s.accept()
    except socket.error:
      is_set_up = True
    
    if not is_set_up:
      print('client connected from', addr)
      cl_file = cl.makefile('rwb', 0)
      while True:
        line = cl_file.readline()
        if not line or line == b'\r\n':
          break
        # TODO: save POST requests to SETTINGS_FILENAME and write confirmation
      response = html % confirmation
      cl.send(response)
      cl.close()
  s.close()

def run_loop(state):
  start = time.ticks_ms()
  while True:
    state.update(time.ticks_diff(start, time.ticks_ms())
    time.sleep_ms(SLEEP_TIME_MS)
    start = time.ticks_ms()

def run(state):    
    wifi_setup()
    
    settings_file = open(SETTINGS_FILENAME)
    essid, password = settings_file.read().split('\n')
    wifi_connect(essid, password)
    run_loop(state)
