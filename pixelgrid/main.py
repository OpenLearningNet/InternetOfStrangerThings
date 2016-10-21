from machine import Pin

D0 = 16
D1 = 5
D2 = 4
D3 = 0
D4 = 2
D5 = 14
D6 = 12
D7 = 13
D8 = 15

leds = Pin(D4, Pin.OUT)
rows = [
    Pin(D1, Pin.OUT),
    Pin(D2, Pin.OUT),
    Pin(D3, Pin.OUT),
    Pin(D0, Pin.OUT)
]
cols = [
    Pin(D5, Pin.IN, Pin.PULL_UP),
    Pin(D6, Pin.IN, Pin.PULL_UP),
    Pin(D7, Pin.IN, Pin.PULL_UP),
    Pin(D8, Pin.IN, Pin.PULL_UP)
]

def all_rows_on():
    for row in rows:
        row.high()

def all_rows_off():
    for row in rows:
        row.low()

def on_keypad_change(pin):
    rows_pressed = []
    all_rows_on()
    for row in rows:
        row.low()
        if pin.value() == 0:
            rows_pressed.append(row)
        row.high()

    print('col', pin, 'rows', rows_pressed)

    all_rows_off()

all_rows_off()
for col in cols:
    col.irq(trigger=Pin.IRQ_FALLING, handler=on_keypad_change)
