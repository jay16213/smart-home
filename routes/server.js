const sendMail = require('../utils/sendMail');
const getIP = require('../utils/getip');
const moment= require('moment');
const request = require('request');

const VALID_FACE = 1;
const NO_FACE = 0;
const INVALID_FACE = -1;
const PI_URL = 'http://192.168.137.220:8080';

module.exports = (app) => {
    let invalidCnt = 0;
    let lastSendTime = 0;

    app.get('/', (req, res, next) => {
        let ip = getIP();
        console.log(`server ip: ${ip}`);
        res.render('index', {ip: ip, pi_url: PI_URL});
    });

    app.post('/face_recognize', (req, res, next) => {
        let result = req.body.result;
        let recognize_status = NO_FACE;

        if(result == VALID_FACE) {
            recognize_status = VALID_FACE;
            invalidCnt = 0;
        }

        else if(result == INVALID_FACE)
            invalidCnt++;

        if(invalidCnt >= 8) {
            let time = moment();
            console.log(`[${time.format('YYYY-MM-DD HH:mm:ss')}] detect stranger`);
            recognize_status = INVALID_FACE;

            // to prevent sending too many mails, send email every 30 minutes
            if(lastSendTime == 0 || time.diff(lastSendTime, 'seconds') >= 1800)
                lastSendTime = sendMail();

            invalidCnt = 0;
        }
        res.end('success');

        request.post(
            `${PI_URL}/face_recognize`,
            { json: {'result': recognize_status} },
            (err, res, body) => {
                if(err) console.log(err);
            }
        );
    });

    app.post('/warning', (req, res) => {
        sendMail();
        res.end('success');
    });
}
