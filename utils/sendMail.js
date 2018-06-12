const nodemailer = require('nodemailer');
const secret = require('../secret/mail');
const moment= require('moment');

module.exports = () => {
    let timestamp;

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
        subject: 'Your Home is in Danger',
        text: 'A stranger is in your house now!\n'
    }

    transporter.sendMail(mailOptions, (err, res) => {
        if(err) throw err;
        timestamp = moment();
        console.log(`${timestamp.format('YYYY-MM-DD HH:mm:ss')} send mail`);
    });

    return timestamp;
}
