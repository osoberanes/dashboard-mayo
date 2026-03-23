const sqlite3 = require('sqlite3').verbose();
const path = require('path');

// Crear base de datos SQLite
const dbPath = path.join(__dirname, '../../database.sqlite');
const db = new sqlite3.Database(dbPath);

// Función para ejecutar queries estilo PostgreSQL
const query = (text, params = []) => {
  return new Promise((resolve, reject) => {
    // Convertir query de PostgreSQL a SQLite
    let sqliteQuery = text
      .replace(/\$(\d+)/g, '?')  // Cambiar $1, $2 por ?
      .replace(/RETURNING \*/g, '')  // SQLite no tiene RETURNING
      .replace(/SERIAL/g, 'INTEGER')
      .replace(/BOOLEAN/g, 'INTEGER')
      .replace(/TEXT\[\]/g, 'TEXT')
      .replace(/TIMESTAMP/g, 'DATETIME')
      .replace(/CURRENT_TIMESTAMP/g, "datetime('now')")
      .replace(/user_role/g, 'TEXT')
      .replace(/solicitud_estado/g, 'TEXT');

    // Si es un INSERT con RETURNING, hacer dos queries
    if (text.includes('RETURNING')) {
      const insertQuery = sqliteQuery.replace(/RETURNING.*$/g, '');
      db.run(insertQuery, params, function(err) {
        if (err) {
          reject(err);
        } else {
          // Obtener el registro insertado
          db.get('SELECT * FROM usuarios WHERE id = ?', [this.lastID], (err, row) => {
            if (err) reject(err);
            else resolve({ rows: row ? [row] : [] });
          });
        }
      });
    } else if (text.toLowerCase().includes('select')) {
      db.all(sqliteQuery, params, (err, rows) => {
        if (err) {
          reject(err);
        } else {
          resolve({ rows: rows || [] });
        }
      });
    } else {
      db.run(sqliteQuery, params, function(err) {
        if (err) {
          reject(err);
        } else {
          resolve({ rows: [], rowCount: this.changes });
        }
      });
    }
  });
};

// Inicializar base de datos con schema básico
const initDatabase = async () => {
  try {
    // Crear tabla usuarios
    await new Promise((resolve, reject) => {
      db.run(`
        CREATE TABLE IF NOT EXISTS usuarios (
          id INTEGER PRIMARY KEY AUTOINCREMENT,
          email TEXT UNIQUE NOT NULL,
          password_hash TEXT NOT NULL,
          nombre TEXT NOT NULL,
          apellidos TEXT NOT NULL,
          rol TEXT DEFAULT 'C',
          departamento_id INTEGER,
          usuario_espejo_id INTEGER,
          fecha_ingreso DATE NOT NULL,
          dias_acumulados REAL DEFAULT 0,
          activo INTEGER DEFAULT 1,
          created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
          updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
      `, (err) => {
        if (err) reject(err);
        else resolve();
      });
    });

    // Verificar si existe usuario admin
    const adminExists = await new Promise((resolve, reject) => {
      db.get('SELECT id FROM usuarios WHERE email = ?', ['admin@empresa.com'], (err, row) => {
        if (err) reject(err);
        else resolve(!!row);
      });
    });

    if (!adminExists) {
      // Insertar usuario admin
      await new Promise((resolve, reject) => {
        db.run(`
          INSERT INTO usuarios (email, password_hash, nombre, apellidos, rol, fecha_ingreso, dias_acumulados, activo)
          VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        `, ['admin@empresa.com', '$2a$10$8K1p/a0dqbQiUHUzrb.UzOd.yzk6pAJrYxoLtM/NnGwPLNfQ8M6iG', 'Administrador', 'Sistema', 'A', '2024-01-01', 25, 1], (err) => {
          if (err) reject(err);
          else resolve();
        });
      });
      console.log('✅ Usuario administrador creado en SQLite');
    }
    
    console.log('✅ Base de datos SQLite inicializada');
  } catch (error) {
    console.error('❌ Error inicializando SQLite:', error);
    throw error;
  }
};

module.exports = {
  query,
  initDatabase,
  db
};