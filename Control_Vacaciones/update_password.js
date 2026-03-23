const sqlite3 = require('sqlite3').verbose();
const path = require('path');

const dbPath = path.join(__dirname, 'database.sqlite');
const db = new sqlite3.Database(dbPath);

const newHash = '$2b$10$bZEvZF2HBPzuRTZ3gkAsgOwOfJTKHeNR6Wu7VBV6Pk6vDxX/mQzd2';

db.run('UPDATE usuarios SET password_hash = ? WHERE email = ?', [newHash, 'admin@empresa.com'], function(err) {
  if (err) {
    console.error('Error:', err);
  } else {
    console.log('✅ Contraseña del administrador actualizada');
    console.log('Filas afectadas:', this.changes);
  }
  db.close();
});