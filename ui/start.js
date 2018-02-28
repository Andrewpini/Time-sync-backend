var express = require('express'),
app = express(),
connection = require('./models/databaseConnection');
app.set('view engine', 'jade');
const sqlQuery = "SELECT * FROM positioning.rssi_data WHERE `IP` LIKE '192.168.14.86' AND `Address` LIKE '00:ce:11:52:a6:0f' AND `Channel` LIKE 39	ORDER BY `ID` DESC";

app.get('/', function (req, res) {
	connection.query(sqlQuery, function(err, rows, fields)
	{
		res.render('rows', {
			items: rows
		});
	});
});



var server = app.listen(8011, function () {

var host = server.address().address;
var port = server.address().port;

console.log('Example app listening at http://%s:%s', host, port);

});