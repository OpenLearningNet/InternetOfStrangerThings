import runtime
import http_client
import pinout

SERVER_ENDPOINT = 'http://gadgets.openlearning.space/cabinet'
DEBOUNCE_TIME = 100
POLLING_TIME = 1000

class Cabinet(object):
  def __init__(self):
    self.button = Pin(pinout.D3, Pin.IN)
    self.lock = Pin(pinout.D2, Pin.OUT)
    self.lamp = Pin(pinout.D1, Pin.OUT)
    
    self.time_until_check = POLLING_TIME
    self.time_until_button_trigger = DEBOUNCE_TIME
    self.last_button_value = 0
    self.is_button_pressed = False
    
  def _update_input(self, delta):
    self.did_button_change = False
    button_value = self.button.value()
    if button_value != self.last_button_value:
      if self.button_trigger <= 0: 
        self.did_button_change = True
        self.last_button_value = button_value
        self.is_button_pressed = bool(button_value)
        self.time_until_button_trigger = DEBOUNCE_TIME
      else:
        self.time_until_button_trigger -= delta
    else:
      self.time_until_button_trigger = DEBOUNCE_TIME
  
  def _update_output(self, delta):
    if self.is_lamp_on:
      self.lamp.high()
    else:
      self.lamp.low()
    
    if self.is_locked:
      self.lock.high()
    else:
      self.lock.low()
  
  def update(self, delta):
    self._update_input(delta)
    
    if self.did_button_change:
      http_client.post(SERVER_ENDPOINT, json={'button': self.is_button_pressed})
    
    if self.time_until_check <=0:
      request = http_client.get(SERVER_ENDPOINT)
      data = request.json()
      self.is_lamp_on = data['lamp']
      self.is_locked  = data['locked']
      
      self.time_until_check = POLLING_TIME
    
    self._update_output(delta)

runtime(Cabinet())
