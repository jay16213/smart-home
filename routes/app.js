var led = require('../gpio/test');
var irSensor = require('../gpio/ir');
var readTemperature = require('../gpio/temp');
var readLightSensor = require('../gpio/light');

module.exports = (app) => {
    app.get('/', (req, res, next) => {
        res.render('index');

        // read ir sensor every 500 ms
        setInterval(irSensor, 500);
    });

    app.post('/led', (req, res) => {
        console.log("click led");
        led();
    });

    app.post('/temp', (req, res) => {
        console.log("read temp");
        readTemperature();
    });

    app.post('/light', (req, res) => {
        let light = readLightSensor();
    });
}
