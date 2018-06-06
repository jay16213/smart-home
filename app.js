const express = require('express');
const ejs = require('ejs');
const engine = require('ejs-mate');

const rpio = require('rpio');
const pin = require('./gpio/pin');

var app = express();

app.use(express.static('public'));
app.use(express.json());
app.engine('ejs', engine);
app.set('view engine', 'ejs');

require('./routes/app')(app);

var server = app.listen(8080, () => {
    console.log('init gpio');
    rpio.open(pin.LIGHT, rpio.OUTPUT, rpio.LOW);
    console.log('listen on port 8080');
});

process.on('SIGINT', () => {
    console.log('handle Ctrl-C');

    console.log('clean up all gpio');
    rpio.close(pin.LIGHT);

    console.log('close server');
    server.close();
    process.exit();
});
