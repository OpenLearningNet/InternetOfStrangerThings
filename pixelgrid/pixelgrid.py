from machine import Pin, Timer
from neopixel import NeoPixel
import math
import server
import time
import gc

D0 = 16
D1 = 5
D2 = 4
D3 = 0
D4 = 2
D5 = 14
D6 = 12
D7 = 13
D8 = 15

leds = NeoPixel(Pin(D8), 16)
colors = [(112,0)] * 16
animation = [6, 7, 8, 14, 13, 11, 4, 2, 1]
rows = [
    Pin(D0, Pin.OUT),
    Pin(D1, Pin.OUT),
    Pin(D2, Pin.OUT),
    Pin(D3, Pin.OUT)
]
cols = [
    Pin(D4, Pin.IN, Pin.PULL_UP),
    Pin(D5, Pin.IN, Pin.PULL_UP),
    Pin(D6, Pin.IN, Pin.PULL_UP),
    Pin(D7, Pin.IN, Pin.PULL_UP)
]
timer = Timer(-1)
cycles_pressed = 0
cycles_since_refresh = 0
cycles_since_throttle = 0
pending_updates = {}
change_to_color = {}
change_to_lum = {}
init_cycles = 0
requires_update = True
requires_refresh = True

PRESS_FOR = 4
REFRESH = 200
THROTTLE = 20

def set_rows(value):
    global rows
    for row in rows:
        row.value(value)

def scan_rows():
    global rows, cols

    buttons_down = []

    set_rows(1)
    for col_index, col in enumerate(cols):
        for row_index, row in enumerate(rows):
            button_index = (3 - row_index) * 4
            if row_index % 2 == 0:
                button_index += col_index
            else:
                button_index += 3 - col_index

            row.low()
            if col.value() == 0:
                buttons_down.append(button_index)

            row.high()
    set_rows(0)

    return buttons_down

def hsl2rgb(h, s, l):
    if l < 128:
        v = (l * (256 + s)) >> 8
    else:
        v = (((l + s) << 8) - l * s) >> 8

    if v <= 0:
        r, g, b = 0, 0, 0
    else:
        m = l + l - v
        h *= 6
        sextant = h >> 8
        fract = h - (sextant << 8)
        vsf = v * fract * (v - m) // v >> 8
        mid1 = m + vsf
        mid2 = v - vsf
        r, g, b = ([
            (v, mid1, m),
            (mid2, v, m),
            (m, v, mid1),
            (m, mid2, v),
            (mid1, m, v),
            (v, m, mid2)
        ])[sextant]

    return r, g, b


def change_light(index):
    global colors, leds
    (h, l) = colors[index]

    if l < 32:
        l = 0
    elif l < 64:
        l = 32
    elif l < 96:
        l = 64
    elif l < 128:
        l = 96
    elif l < 160:
        l = 128
    elif l < 192:
        l = 160
    else:
        l = 192

    r, g, b = hsl2rgb(h, 255, l)
    leds[index] = (g, r, b)

def update(timer):
    global colors, leds, cycles_pressed, cycles_since_refresh, cycles_since_throttle
    global pending_updates, change_to_color, change_to_lum, init_cycles
    global requires_update

    if init_cycles <= len(animation):
        for i in animation[:init_cycles]:
            colors[i] = (112, 128)
            change_light(i)
        leds.write()

        init_cycles += 1
        return

    buttons = scan_rows()
    requires_write = False
    for button in buttons:
        h, l = colors[button]

        if cycles_pressed == 0:
            h += 16
            h = h % 256
            change_to_color[button] = h
        elif cycles_pressed > PRESS_FOR:
            l += 8
            l = l % 192
            if button in change_to_color:
                del change_to_color[button]

            change_to_lum[button] = l

            # Update LEDs right away
            colors[button] = (h, l)
            change_light(button)
            requires_write = True

    if len(buttons) > 0:
        cycles_pressed += 1
    else:
        if cycles_pressed != 0:
            # On Release
            for index, hue in change_to_color.items():
                h, l = colors[index]
                pending_updates[str(index)] = (hue, l)

                # Update LEDs
                colors[index] = (hue, l)
                change_light(index)
                requires_write = True

            for index in change_to_color.keys():
                del change_to_color[index]

            for index, lum in change_to_lum.items():
                h, l = colors[index]
                pending_updates[str(index)] = (h, lum)

            for index in change_to_lum.keys():
                del change_to_lum[index]

            #print('Color Changed')

        cycles_pressed = 0

    if requires_write:
        leds.write()

    cycles_since_refresh += 1
    if cycles_since_refresh > REFRESH and len(buttons) == 0:
        requires_refresh = True
        cycles_since_refresh = 0

    cycles_since_throttle += 1
    if cycles_since_throttle > THROTTLE and len(buttons) == 0:
        requires_update = True
        cycles_since_throttle = 0

def init(url):
    global timer, leds, pending_updates, requires_update, requires_refresh, colors
    set_rows(0)
    print('Setting up...')
    timer.init(period=100, mode=Timer.PERIODIC, callback=update)
    for color in range(16):
        change_light(color)
    leds.write()

    url_parts = url.split(':', 2)
    host = url_parts[0]
    port = int(url_parts[1])

    connection = server.init(host, port)
    errors_occurred = 0

    received_updates = True

    while True:
        try:
            if requires_update:
                if len(pending_updates) > 0:
                    server.send(connection, pending_updates)
                    pending_updates = {}

                if received_updates:
                    leds.write()
                    received_updates = False

                requires_update = False

            if requires_refresh:
                server.request(connection)
                requires_refresh = False

            try:
                new_data = server.recv(connection)
            except Exception:
                new_data = {}

            if new_data is None:
                errors_occurred += 1
                new_data = {}
            else:
                errors_occurred = 0

            if len(new_data) > 0:
                for key, val in new_data.items():
                    index = int(key)
                    if key not in pending_updates:
                        colors[index] = val
                        change_light(index)
                        print('Changing', key, val)
                    else:
                        print('Skipping', key, pending_updates)
                received_updates = True

            if errors_occurred > 100:
                errors_occurred = 0
                requires_refresh = True
                raise Exception("Resetting")

        except Exception as err:
            print(err)
            server.end(connection)
            connection = server.init(host, port)

        gc.collect()
