import usocket

def init(host, port, path):
    addr_info = usocket.getaddrinfo(host, port)
    addr = addr_info[0][4]
    return (addr, path, host)

def recv(connection):
    return send(connection, None, method='GET')

def send(connection, data, method='POST'):
    addr, path, host = connection

    sock = usocket.socket()
    sock.connect(addr)
    sock.write('%s /%s HTTP/1.0\r\nHost: %s\r\n' % (method, path, host))

    if data is not None:
        sock.write('content-length: %s\r\n' % len(data))
        sock.write('\r\n')
        sock.write(data)
    else:
        sock.write('\r\n')

    l = sock.readline()
    _, status, msg = l.split(None, 2)

    while sock.readline() != b'\r\n':
        pass

    content = sock.read()
    sock.close()
    return content.decode('utf-8')
