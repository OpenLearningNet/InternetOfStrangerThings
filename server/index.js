var express = require('express');
var bodyParser = require('body-parser');
var app = express();

app.use(bodyParser.text({type: '*/*'}));

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

app.get('/pixels', function (req, res) {
  const dataPairs = pixel_data.map((pair) => pair.join(';'));
  const data = dataPairs.join(',');
  res.send(data);
});

/*
app.get('/pixels', function (req, res) {
  const buf = new Buffer();
  res.send(buf);
});
*/

app.post('/pixels', function (req, res) {

  req.body.split(',').forEach((item) => {
    const keyVal = item.split(':')
    const vals = keyVal[1].split(';');
    const index = parseInt(keyVal[0], 10);
    pixel_data[index] = [
      parseInt(vals[0], 10),
      parseInt(vals[1], 10)
    ];
  });
  res.send('OK');
});

app.listen(3000, function () {
  console.log('Example app listening on port 3000!')
})
