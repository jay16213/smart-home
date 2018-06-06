const rpio = require('rpio');
const IR_PIN = require('./pin').IR;

var irSensor = () => {
    rpio.open(IR_PIN, rpio.INPUT);

    let res = rpio.read(IR_PIN);
    if(res == 1)
        console.log(new Date().toString() + ": motion detected");
    // console.log('Pin 22 = %d', rpio.read(IR_PIN));
    rpio.close(IR_PIN);
    return;
}

module.exports = irSensor;
