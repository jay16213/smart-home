const led = require('../gpio/test');
const irSensor = require('../gpio/ir');
const readTemperature = require('../gpio/temp');
const readLightSensor = require('../gpio/light');
const sendMail = require('../utils/sendMail');
const getIP = require('../utils/getip');
const moment= require('moment');

const VALID_FACE = 1;
const NO_FACE = 0;
const INVALID_FACE = -1;

module.exports = (app) => {
    let invalidCnt = 0;
    let lastSendTime = 0;

    app.get('/', (req, res, next) => {
        // read ir sensor every 500 ms
        setInterval(irSensor, 500);
        let ip = getIP();
        console.log(`server ip: ${ip}`);
        res.render('index', {ip: ip});
    });

    app.post('/led', (req, res) => {
        console.log("click led");
        led();
        res.end('success');
    });

    app.post('/temp', (req, res) => {
        console.log("read temp");
        readTemperature();
        res.end('success');
    });

    app.post('/light', (req, res) => {
        let light = readLightSensor();
    });

    app.post('/face_recognize', (req, res) => {
        let result = req.body.result;

        if(result == VALID_FACE)
            invalidCnt = 0;

        if(result == INVALID_FACE)
            invalidCnt++;

        if(invalidCnt >= 5)
        {
            let time = moment();
            console.log(`[${time.format('YYYY-MM-DD HH:mm:ss')}] detect stranger`);

            // to prevent sending too many mails, send email every 30 minutes
            if(lastSendTime == 0 || time.diff(lastSendTime, 'seconds') >= 1800)
                lastSendTime = sendMail();

            invalidCnt = 0;
        }

        res.end('success');
    });

    app.post('/warning', (req, res) => {
        sendMail();
        res.end('success');
    });
}
