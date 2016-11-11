import pixelgrid
import network
import captive
import os

def do_connect(essid, password):
    import network
    sta_if = network.WLAN(network.STA_IF)
    if not sta_if.isconnected():
        print('Connecting to network...')
        sta_if.active(True)
        sta_if.connect(essid, password)
        while not sta_if.isconnected():
            pass
    a, b, c, d = sta_if.ifconfig()
    sta_if.ifconfig((a, b, c, '8.8.8.8'))

    print('Network config:', sta_if.ifconfig())

params = captive.init('PixelTron', 'swordfish')


if params is not None:
    essid = params.get('essid', '')
    password = params.get('password', '')
    server = params.get('server', '').replace('%2F', '/').replace('%2f', '/')
    server = server.replace('%3A', ':').replace('%3a', ':')
    print('Writing Setup')
    f = open('setup.txt', 'w')
    f.write(essid + '\n' + password + '\n' + server)
    f.close()
else:
    f = open('setup.txt', 'r')
    setup = f.read()
    essid, password, server = setup.split('\n')[:3]
    f.close()
    print('Read Setup')

print('Connecting: ', essid, password)
do_connect(essid, password)

print('Running with', server)
pixelgrid.init(server)
