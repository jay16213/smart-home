const led = require('../gpio/test');
const irSensor = require('../gpio/ir');
const readTemperature = require('../gpio/temp');
const readLightSensor = require('../gpio/light');
const nodemailer = require('nodemailer');
const secret = require('../secret/mail');

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

    app.post('/warning', (req, res) => {
        let transporter = nodemailer.createTransport({
            service: 'Gmail',
            auth: {
                user: secret.user,
                pass: secret.password
            }
        });

        let mailOptions = {
            to: `${secret.user}@gmail.com`,
            from: `SmartHome <${secret.user}>`,
            subject: 'Your Home Has Danger',
            text: 'A stranger is in your house now!\n'
        }

        transporter.sendMail(mailOptions, (err, res) => {
            if(err) throw err;
            console.log("send mail!");
        });
    });
}
