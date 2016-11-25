import usocket
import time

def init(host, port):
    addr_info = usocket.getaddrinfo(host, port)
    addr = addr_info[0][4]

    is_connected = False

    while not is_connected:
        try:
            sock = usocket.socket()
            sock.settimeout(2)
            print('Connecting to', addr)
            sock.connect(addr)
            is_connected = True
        except OSError as err:
            print(err)
            print('Trying again in 10s')
            time.sleep(10)

    print('Connected!')
    return sock

def request(connection):
    sock = connection
    sock.write('GET\n')

def recv(connection):
    sock = connection

    data = None

    line = sock.readline().decode('utf-8')
    if line.startswith('SET>'):
        data = {}
        payload = line.split('SET>')[1].split(':')
        data[payload[0]] = tuple(int(item) for item in payload[1].split(','))

    print('Received', data)
    return data

def send(connection, data):
    sock = connection
    payload = []
    for key, val in data.items():
        sock.write('SET>' + str(key) + ':' + ','.join(str(v) for v in val) + '\n')
    print('Sent', data)

def end(connection):
    connection.close()
