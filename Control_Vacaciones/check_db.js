const sqlite3 = require('sqlite3').verbose();
const path = require('path');

const dbPath = path.join(__dirname, 'database.sqlite');
const db = new sqlite3.Database(dbPath);

db.all('SELECT * FROM usuarios', [], (err, rows) => {
  if (err) {
    console.error('Error:', err);
  } else {
    console.log('Usuarios en la base de datos:');
    console.log(rows);
  }
  db.close();
});