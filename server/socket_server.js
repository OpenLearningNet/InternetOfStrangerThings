// Load the TCP Library
net = require('net');

var clients = [];

const pixel_data = [
  [112, 128],
  [112, 128],
  [112, 128],
  [112, 128],
  [112, 128],
  [112, 128],
  [112, 128],
  [112, 128],
  [112, 128],
  [112, 128],
  [112, 128],
  [112, 128],
  [112, 128],
  [112, 128],
  [112, 128],
  [112, 128]
];

// Start a TCP Server
net.createServer(function (socket) {

  // Identify this client
  socket.name = socket.remoteAddress + ":" + socket.remotePort
  socket.buffer = '';

  // Put this new client in the list
  clients.push(socket);
  socket.write("HI\n\n");
  process.stdout.write(socket.name + ' connected.\n');

  // Handle incoming messages from clients.
  socket.on('data', function (data) {
    data = data.toString();

    process.stdout.write('Received from ' + socket.name + '\n');
    process.stdout.write(data + '\n');

    if (data == 'GET\n') {
      const data_array = pixel_data.map((item) => item.join(','));
      data_array.forEach((item, i) => {
        socket.write('SET>' + i + ':' + item + '\n');
      });
    } else if (data.startsWith('SET>')) {
      const payload = data.split('SET>')[1];
      const keyVal = payload.split(':');
      const values = keyVal[1].split(',');
      const index = parseInt(keyVal[0], 10);
      pixel_data[index] = values;
      broadcast(data, socket);
    } else {
      console.log('Unknown command: ', data);
    }
  });

  // Remove the client from the list when it leaves
  socket.on('end', function () {
    clients.splice(clients.indexOf(socket), 1);
    process.stdout.write(socket.name + " disconnected.\n");
  });

  // Send a message to all clients
  function broadcast(message, sender) {
    clients.forEach(function (client) {
      // Don't want to send it to sender
      if (client === sender) return;
      client.write(message);
    });
    // Log it to the server output too
    process.stdout.write(message)
  }
}).listen(5000);

// Put a friendly message on the terminal of the server.
console.log("Pixel server running at port 5000\n");
