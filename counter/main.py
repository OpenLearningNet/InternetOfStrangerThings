from machine import Pin, SPI
import network
import time
import webrepl

D5 = 14
D6 = 12
D7 = 13

DIN = Pin(D7, Pin.OUT)
CS  = Pin(D6, Pin.OUT)
CLK = Pin(D5, Pin.OUT)

MAXREG_DECODEMODE = 0x09
MAXREG_INTENSITY  = 0x0a
MAXREG_SCANLIMIT  = 0x0b
MAXREG_SHUTDOWN   = 0x0c
MAXREG_DISPTEST   = 0x0f

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

wifi_connect('openlearning.com', 'AbsurdCyclicDungeonPipe')
webrepl.start()

spi = SPI(1, polarity=0, phase=0)

CS.low()
spi.write(bytearray[0x0F, 0x01])
CS.high()
