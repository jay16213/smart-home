const irSensor = require('../gpio/ir');
const readTemperature = require('../gpio/temp');
const buzzer = require('../gpio/buzzer');
const getIP = require('../utils/getip');
const moment= require('moment');
const rpio = require('rpio');
const pin = require('../gpio/pin');

const VALID_FACE = 1;
const NO_FACE = 0;
const INVALID_FACE = -1;

module.exports = (app) => {
    let invalidCnt = 0;
    let lastSendTime = 0;

    app.all('*', (req, res, next) => {
        res.header("Access-Control-Allow-Origin", "*");
        res.header("Access-Control-Allow-Headers", "X-Requested-With");
        next();
    });

    app.post('/temp', (req, res) => {
        console.log("read temp");
        readTemperature();
        res.end('success');
    });

    app.post('/open/light', (req, res) => {
        rpio.write(pin.LIGHT, rpio.HIGH);
        res.end('success');
    });

    app.post('/close/light', (req, res) => {
        rpio.write(pin.LIGHT, rpio.LOW);
        res.end('success');
    });

    app.post('/buzzer', (req, res) => {
        buzzer();
        res.end('success');
    });
}
