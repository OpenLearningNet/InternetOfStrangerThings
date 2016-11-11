import usocket

def init(host, port):
    addr_info = usocket.getaddrinfo(host, port)
    addr = addr_info[0][4]
    sock = usocket.socket()
    sock.settimeout(2)
    sock.connect(addr)
    print('Connected to', addr)
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
