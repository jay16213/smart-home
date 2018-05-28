const rpio = require('rpio');

const LED_R = 12;

var led = function() {
    rpio.open(LED_R, rpio.OUTPUT, rpio.LOW);

    for(var i = 0; i < 5; i++) {
        rpio.write(LED_R, rpio.HIGH);
        rpio.msleep(500);
        rpio.write(LED_R, rpio.LOW);
        rpio.msleep(500);
    }

    rpio.close(LED_R);
}

module.exports = led;
