var mysql = require('mysql');
module.exports = mysql.createConnection({
  host     : 'localhost',
  user     : 'root',
  password : 'admin',
  database : 'positioning',
  dateStrings: 'date'
});