var led = require('../gpio/test');

module.exports = (app) => {
    app.get('/', (req, res, next) => {
        res.render('index');
    });

    app.post('/led', (req, res) => {
        console.log("click led");
        led();
    });
}
