// Load the TCP Library
var net = require('net');

// for Web APIs
var express = require('express')
var app = express()
var bodyParser = require('body-parser');

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


// Web API
app.use(bodyParser.urlencoded());
app.use(bodyParser.json());

app.get('/', function (req, res) {
  res.json({
    pixels: pixel_data
  });
});
app.post('/', function(req, res) {
  var index = parseInt(req.body.index, 10);
  var hue = parseInt(req.body.hue, 10);
  var lum = parseInt(req.body.lum, 10);
  var didSet = false;
  if (index < pixel_data.length && index >= 0) {
    hue = hue % 256;
    lum = lum % 256;
    pixel_data[index] = [hue, lum];
    didSet = true;
  }
  updateAll();
  res.json({
    success: didSet,
    pixels: pixel_data
  });
});

// Start Web Server
app.listen(3210, function () {
  console.log('Web Server Running on 3210')
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

// Update all clients
function updateAll() {
  const data_array = pixel_data.map((item) => item.join(','));
  data_array.forEach((item, i) => {
    broadcast('SET>' + i + ':' + item + '\n', null);
  });
}

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
}).listen(5000);

// Put a friendly message on the terminal of the server.
console.log("Pixel server running at port 5000\n");
