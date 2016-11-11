import socket
import network
import time

CONTENT = b"""\
HTTP/1.0 200 OK\r\n
<!doctype html>
<html>
    <head>
        <title>PixelTron Setup</title>
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <meta charset="utf8">
    </head>
    <body>
        <form action="/set">
            <input type="text" placeholder="ESSID" name="essid" />
            <input type="text" placeholder="Password" name="password" />
            <input type="text" placeholder="Server" name="server" />
            <input type="submit" value="Save" />
        </form>
    </body>
</html>
"""

class DNSQuery:
  def __init__(self, data):
    self.data=data
    self.dominio=''

    print("Reading datagram data...")
    m = data[2] # ord(data[2])
    tipo = (m >> 3) & 15   # Opcode bits
    if tipo == 0:                     # Standard query
      ini=12
      lon=data[ini] # ord(data[ini])
      while lon != 0:
        self.dominio+=data[ini+1:ini+lon+1].decode("utf-8") +'.'
        ini+=lon+1
        lon=data[ini] #ord(data[ini])

  def respuesta(self, ip):
    packet=b''
    print("Resposta {} == {}".format(self.dominio, ip))
    if self.dominio:
      packet+=self.data[:2] + b"\x81\x80"
      packet+=self.data[4:6] + self.data[4:6] + b'\x00\x00\x00\x00'   # Questions and Answers Counts
      packet+=self.data[12:]                                         # Original Domain Name Question
      packet+= b'\xc0\x0c'                                             # Pointer to domain name
      packet+= b'\x00\x01\x00\x01\x00\x00\x00\x3c\x00\x04'             # Response type, ttl and resource data length -> 4 bytes
      packet+=bytes(map(int,ip.split('.'))) # 4 bytes of IP
    return packet

def init(essid, password):
    ap = network.WLAN(network.AP_IF)
    ap.active(True)
    ap.config(essid=essid, password=password, authmode=4) #authmode=1 == no pass
    ap.ifconfig(('192.168.0.1', '255.255.255.0', '192.168.0.1', '192.168.0.1'))
    ip = ap.ifconfig()[0]

    counter = 0

    udps = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    udps.setblocking(False)
    udps.bind(('',53))

    s = socket.socket()
    ai = socket.getaddrinfo(ip, 80)
    addr = ai[0][-1]
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind(addr)
    s.listen(1)
    s.settimeout(2)

    print("Web Server: Listening http://{}:80/".format(ip))
    is_running = True

    return_params = None

    while is_running:
        try:
            data, addr = udps.recvfrom(1024)
            print("incomming datagram...")
            p=DNSQuery(data)
            udps.sendto(p.respuesta(ip), addr)
            print('Replying: {:s} -> {:s}'.format(p.dominio, ip))
        except:
            print("No dgram")

        try:
            res = s.accept()
            client_sock = res[0]
            client_addr = res[1]

            client_stream = client_sock

            print("Request:")
            req = client_stream.readline()
            print(req)
            while True:
                h = client_stream.readline()
                if h == b"" or h == b"\r\n" or h == None:
                    break
                print(h)

            request_url = req[4:-11]
            api = request_url[:5]
            if api == b'/set?':
                params = request_url[5:]
                try:
                    return_params = {key.decode('utf-8'): value.decode('utf-8') for (key, value) in [x.split(b'=') for x in params.split(b'&')]}
                except:
                    return_params = None

                if return_params is not None:
                    is_running = False

            print("Response:")
            print(CONTENT)

            client_stream.write(CONTENT)
            client_stream.close()
        except:
            print("timeout for web... moving on...")
            counter += 1

        try:
          time.sleep_ms(300)
        except KeyboardInterrupt:
          is_running = False

        if counter >= 20:
          is_running = False
    udps.close()
    ap.active(False)

    return return_params
