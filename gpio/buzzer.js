const rpio = require('rpio');
const BUZZER_PIN = require('./pin').BUZZER;

module.exports = () => {
    rpio.open(BUZZER_PIN, rpio.OUTPUT, rpio.LOW);

    for(let i = 0; i < 10; i++)
    {
        rpio.write(BUZZER_PIN, rpio.HIGH);
        rpio.msleep(250);
        rpio.write(BUZZER_PIN, rpio.LOW);
        rpio.msleep(250);
    }

    rpio.close(BUZZER_PIN);
    return;
}
