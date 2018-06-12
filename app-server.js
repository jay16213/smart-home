const express = require('express');
const ejs = require('ejs');
const engine = require('ejs-mate');

var app = express();

app.use(express.static('public'));
app.use(express.json());
app.engine('ejs', engine);
app.set('view engine', 'ejs');

require('./routes/server')(app);

var server = app.listen(8080, () => {
    console.log('listen on port 8080');
});

process.on('SIGINT', () => {
    console.log('handle Ctrl-C');
    console.log('close server');
    server.close();
    process.exit();
});
