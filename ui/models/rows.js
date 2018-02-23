var rows;
var connection = require('./databaseConnection');
var http = require('http');

rows = function() {
  http.createServer(function (request, response) 
  { 
    console.log('Creating the http server');
    connection.query('SELECT * FROM rssi_data', function(err, rows, fields)
    {
      response.writeHead(200, { 'Content-Type': 'application/json'});
      var row = response.end(JSON.stringify(rows));
      return row;
    }); 
   });
}

module.exports = rows();