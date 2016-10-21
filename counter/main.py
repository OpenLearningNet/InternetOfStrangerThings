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
