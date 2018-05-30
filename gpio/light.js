const rpio = require('rpio');
const LIGHT_SENSOR_PIN = 29;

var readLightSensor = () => {
    rpio.open(LIGHT_SENSOR_PIN, rpio.INPUT);

    let light = rpio.read(LIGHT_SENSOR_PIN);
    console.log("light: " + light);
    rpio.close(LIGHT_SENSOR_PIN);

    return light;
}

module.exports = readLightSensor;
