// Configuración temporal con SQLite
const sqlite3 = require('sqlite3').verbose();
const path = require('path');

const dbPath = path.join(__dirname, '../../database.sqlite');
const db = new sqlite3.Database(dbPath);

// Función query simplificada
const query = (text, params = []) => {
  return new Promise((resolve, reject) => {
    // Convertir query básico de PostgreSQL a SQLite
    let sqliteQuery = text.replace(/\$(\d+)/g, '?');
    
    if (text.toLowerCase().includes('select')) {
      db.all(sqliteQuery, params, (err, rows) => {
        if (err) reject(err);
        else resolve({ rows: rows || [] });
      });
    } else {
      db.run(sqliteQuery, params, function(err) {
        if (err) reject(err);
        else resolve({ rows: [], rowCount: this.changes });
      });
    }
  });
};

// Crear tabla usuarios si no existe
db.serialize(() => {
  db.run(`
    CREATE TABLE IF NOT EXISTS usuarios (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      email TEXT UNIQUE NOT NULL,
      password_hash TEXT NOT NULL,
      nombre TEXT NOT NULL,
      apellidos TEXT NOT NULL,
      rol TEXT DEFAULT 'C',
      departamento_id INTEGER,
      fecha_ingreso TEXT NOT NULL,
      dias_acumulados REAL DEFAULT 0,
      activo INTEGER DEFAULT 1
    )
  `);
  
  // Insertar admin si no existe
  db.get('SELECT id FROM usuarios WHERE email = ?', ['admin@empresa.com'], (err, row) => {
    if (!err && !row) {
      db.run(`
        INSERT INTO usuarios (email, password_hash, nombre, apellidos, rol, fecha_ingreso, dias_acumulados, activo)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
      `, ['admin@empresa.com', '$2b$10$bZEvZF2HBPzuRTZ3gkAsgOwOfJTKHeNR6Wu7VBV6Pk6vDxX/mQzd2', 'Administrador', 'Sistema', 'A', '2024-01-01', 25, 1]);
    }
  });
});

console.log('🔄 Usando SQLite temporal para desarrollo');

module.exports = {
  query
};