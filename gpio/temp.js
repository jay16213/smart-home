const sensor = require('node-dht-sensor');

const DHT11_PGIO = 4;

var readTemperature = () => {
    sensor.read(11, DHT11_PGIO, function(err, temperature, humidity) {
        if(err) throw err;

        console.log('temp: ' + temperature.toFixed(1) + ' C');
    });
}

module.exports = readTemperature;
