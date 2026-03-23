const express = require('express');
const cors = require('cors');
const bcrypt = require('bcryptjs');
const jwt = require('jsonwebtoken');
const sqlite3 = require('sqlite3').verbose();
const path = require('path');

require('dotenv').config();

const app = express();
app.use(cors());
app.use(express.json());

const dbPath = path.join(__dirname, 'database.sqlite');
const db = new sqlite3.Database(dbPath);

// Crear tablas necesarias
db.serialize(() => {
  // Tabla de departamentos
  db.run(`
    CREATE TABLE IF NOT EXISTS departamentos (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      nombre TEXT NOT NULL,
      activo INTEGER DEFAULT 1
    )
  `);

  // Tabla de solicitudes de vacaciones
  db.run(`
    CREATE TABLE IF NOT EXISTS solicitudes_vacaciones (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      usuario_id INTEGER NOT NULL,
      fecha_inicio TEXT NOT NULL,
      fecha_fin TEXT NOT NULL,
      dias_solicitados INTEGER NOT NULL,
      motivo TEXT,
      estado TEXT DEFAULT 'pendiente',
      aprobado_por INTEGER,
      fecha_aprobacion TEXT,
      comentarios_aprobacion TEXT,
      fecha_creacion TEXT DEFAULT CURRENT_TIMESTAMP,
      fecha_actualizacion TEXT DEFAULT CURRENT_TIMESTAMP,
      FOREIGN KEY (usuario_id) REFERENCES usuarios (id),
      FOREIGN KEY (aprobado_por) REFERENCES usuarios (id)
    )
  `);

  // Tabla de días festivos
  db.run(`
    CREATE TABLE IF NOT EXISTS dias_festivos (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      fecha TEXT NOT NULL,
      nombre TEXT NOT NULL,
      activo INTEGER DEFAULT 1
    )
  `);

  // Insertar departamentos por defecto
  db.get('SELECT id FROM departamentos WHERE nombre = ?', ['Administración'], (err, row) => {
    if (!err && !row) {
      db.run('INSERT INTO departamentos (nombre) VALUES (?)', ['Administración']);
      db.run('INSERT INTO departamentos (nombre) VALUES (?)', ['Recursos Humanos']);
      db.run('INSERT INTO departamentos (nombre) VALUES (?)', ['Ventas']);
      db.run('INSERT INTO departamentos (nombre) VALUES (?)', ['Marketing']);
      db.run('INSERT INTO departamentos (nombre) VALUES (?)', ['IT']);
    }
  });

  // Insertar algunos días festivos por defecto
  db.get('SELECT id FROM dias_festivos WHERE fecha = ?', ['2024-01-01'], (err, row) => {
    if (!err && !row) {
      db.run('INSERT INTO dias_festivos (fecha, nombre) VALUES (?, ?)', ['2024-01-01', 'Año Nuevo']);
      db.run('INSERT INTO dias_festivos (fecha, nombre) VALUES (?, ?)', ['2024-05-01', 'Día del Trabajo']);
      db.run('INSERT INTO dias_festivos (fecha, nombre) VALUES (?, ?)', ['2024-09-16', 'Día de la Independencia']);
      db.run('INSERT INTO dias_festivos (fecha, nombre) VALUES (?, ?)', ['2024-12-25', 'Navidad']);
    }
  });
});

app.post('/api/auth/login', async (req, res) => {
  try {
    console.log('📥 Login request received:', req.body);
    
    const { email, password } = req.body;
    
    if (!email || !password) {
      console.log('❌ Missing email or password');
      return res.status(400).json({ error: 'Email y contraseña son requeridos' });
    }

    console.log('🔍 Searching for user:', email);
    
    // Buscar usuario
    db.get('SELECT * FROM usuarios WHERE email = ?', [email.toLowerCase()], async (err, user) => {
      if (err) {
        console.error('❌ Database error:', err);
        return res.status(500).json({ error: 'Error de base de datos' });
      }

      if (!user) {
        console.log('❌ User not found');
        return res.status(401).json({ error: 'Credenciales inválidas' });
      }

      console.log('✅ User found:', { id: user.id, email: user.email, role: user.rol });

      if (!user.activo) {
        console.log('❌ User inactive');
        return res.status(401).json({ error: 'Usuario inactivo' });
      }

      try {
        console.log('🔐 Comparing passwords...');
        const passwordMatch = await bcrypt.compare(password, user.password_hash);
        console.log('🔐 Password match:', passwordMatch);

        if (!passwordMatch) {
          console.log('❌ Invalid password');
          return res.status(401).json({ error: 'Credenciales inválidas' });
        }

        // Generar token
        console.log('🎫 Generating JWT token...');
        const token = jwt.sign(
          { userId: user.id, email: user.email, rol: user.rol },
          process.env.JWT_SECRET || 'fallback_secret',
          { expiresIn: '24h' }
        );

        console.log('✅ Login successful');
        res.json({
          message: 'Login exitoso',
          token,
          user: {
            id: user.id,
            email: user.email,
            nombre: user.nombre,
            apellidos: user.apellidos,
            rol: user.rol,
            departamento_nombre: 'N/A'
          }
        });
      } catch (passwordError) {
        console.error('❌ Password comparison error:', passwordError);
        return res.status(500).json({ error: 'Error verificando contraseña' });
      }
    });

  } catch (error) {
    console.error('❌ Login error:', error);
    res.status(500).json({ error: 'Error interno del servidor', details: error.message });
  }
});

// Verificar token
app.get('/api/auth/verify', (req, res) => {
  try {
    const authHeader = req.headers.authorization;
    if (!authHeader || !authHeader.startsWith('Bearer ')) {
      return res.status(401).json({ error: 'Token no encontrado' });
    }

    const token = authHeader.split(' ')[1];
    const decoded = jwt.verify(token, process.env.JWT_SECRET || 'fallback_secret');
    
    console.log('🎫 Token verified for user:', decoded.email);
    res.json({ 
      valid: true, 
      user: {
        id: decoded.userId,
        email: decoded.email,
        rol: decoded.rol
      }
    });
  } catch (error) {
    console.error('❌ Token verification failed:', error.message);
    res.status(401).json({ error: 'Token inválido' });
  }
});

// API de solicitudes de vacaciones
app.get('/api/solicitudes', (req, res) => {
  try {
    const authHeader = req.headers.authorization;
    if (!authHeader || !authHeader.startsWith('Bearer ')) {
      return res.status(401).json({ error: 'Token no encontrado' });
    }

    const token = authHeader.split(' ')[1];
    const decoded = jwt.verify(token, process.env.JWT_SECRET || 'fallback_secret');
    
    let query = `
      SELECT s.*, u.nombre || ' ' || u.apellidos as usuario_nombre,
             ua.nombre || ' ' || ua.apellidos as aprobado_por_nombre
      FROM solicitudes_vacaciones s
      JOIN usuarios u ON s.usuario_id = u.id
      LEFT JOIN usuarios ua ON s.aprobado_por = ua.id
    `;
    
    if (decoded.rol === 'C') {
      query += ' WHERE s.usuario_id = ?';
      db.all(query, [decoded.userId], (err, rows) => {
        if (err) {
          console.error('Error fetching solicitudes:', err);
          return res.status(500).json({ error: 'Error de base de datos' });
        }
        res.json(rows || []);
      });
    } else {
      db.all(query, (err, rows) => {
        if (err) {
          console.error('Error fetching solicitudes:', err);
          return res.status(500).json({ error: 'Error de base de datos' });
        }
        res.json(rows || []);
      });
    }
  } catch (error) {
    console.error('Error in solicitudes endpoint:', error);
    res.status(401).json({ error: 'Token inválido' });
  }
});

app.post('/api/solicitudes', (req, res) => {
  try {
    const authHeader = req.headers.authorization;
    if (!authHeader || !authHeader.startsWith('Bearer ')) {
      return res.status(401).json({ error: 'Token no encontrado' });
    }

    const token = authHeader.split(' ')[1];
    const decoded = jwt.verify(token, process.env.JWT_SECRET || 'fallback_secret');
    
    const { fecha_inicio, fecha_fin, dias_solicitados, motivo } = req.body;
    
    if (!fecha_inicio || !fecha_fin || !dias_solicitados) {
      return res.status(400).json({ error: 'Datos requeridos faltantes' });
    }

    // Validaciones básicas
    const inicio = new Date(fecha_inicio);
    const fin = new Date(fecha_fin);
    const hoy = new Date();
    
    if (inicio < hoy) {
      return res.status(400).json({ error: 'La fecha de inicio no puede ser en el pasado' });
    }
    
    if (fin <= inicio) {
      return res.status(400).json({ error: 'La fecha de fin debe ser posterior a la de inicio' });
    }

    db.run(
      `INSERT INTO solicitudes_vacaciones 
       (usuario_id, fecha_inicio, fecha_fin, dias_solicitados, motivo, fecha_creacion)
       VALUES (?, ?, ?, ?, ?, CURRENT_TIMESTAMP)`,
      [decoded.userId, fecha_inicio, fecha_fin, dias_solicitados, motivo],
      function(err) {
        if (err) {
          console.error('Error creating solicitud:', err);
          return res.status(500).json({ error: 'Error creando solicitud' });
        }
        
        res.status(201).json({
          message: 'Solicitud creada exitosamente',
          id: this.lastID
        });
      }
    );
  } catch (error) {
    console.error('Error in create solicitud:', error);
    res.status(401).json({ error: 'Token inválido' });
  }
});

app.put('/api/solicitudes/:id/aprobar', (req, res) => {
  try {
    const authHeader = req.headers.authorization;
    if (!authHeader || !authHeader.startsWith('Bearer ')) {
      return res.status(401).json({ error: 'Token no encontrado' });
    }

    const token = authHeader.split(' ')[1];
    const decoded = jwt.verify(token, process.env.JWT_SECRET || 'fallback_secret');
    
    if (decoded.rol === 'C') {
      return res.status(403).json({ error: 'No tienes permisos para aprobar solicitudes' });
    }

    const { comentarios } = req.body;
    const solicitudId = req.params.id;

    db.run(
      `UPDATE solicitudes_vacaciones 
       SET estado = 'aprobada', aprobado_por = ?, fecha_aprobacion = CURRENT_TIMESTAMP, 
           comentarios_aprobacion = ?, fecha_actualizacion = CURRENT_TIMESTAMP
       WHERE id = ?`,
      [decoded.userId, comentarios, solicitudId],
      function(err) {
        if (err) {
          console.error('Error approving solicitud:', err);
          return res.status(500).json({ error: 'Error aprobando solicitud' });
        }
        
        if (this.changes === 0) {
          return res.status(404).json({ error: 'Solicitud no encontrada' });
        }
        
        res.json({ message: 'Solicitud aprobada exitosamente' });
      }
    );
  } catch (error) {
    console.error('Error in approve solicitud:', error);
    res.status(401).json({ error: 'Token inválido' });
  }
});

app.put('/api/solicitudes/:id/rechazar', (req, res) => {
  try {
    const authHeader = req.headers.authorization;
    if (!authHeader || !authHeader.startsWith('Bearer ')) {
      return res.status(401).json({ error: 'Token no encontrado' });
    }

    const token = authHeader.split(' ')[1];
    const decoded = jwt.verify(token, process.env.JWT_SECRET || 'fallback_secret');
    
    if (decoded.rol === 'C') {
      return res.status(403).json({ error: 'No tienes permisos para rechazar solicitudes' });
    }

    const { comentarios } = req.body;
    const solicitudId = req.params.id;

    db.run(
      `UPDATE solicitudes_vacaciones 
       SET estado = 'rechazada', aprobado_por = ?, fecha_aprobacion = CURRENT_TIMESTAMP,
           comentarios_aprobacion = ?, fecha_actualizacion = CURRENT_TIMESTAMP
       WHERE id = ?`,
      [decoded.userId, comentarios, solicitudId],
      function(err) {
        if (err) {
          console.error('Error rejecting solicitud:', err);
          return res.status(500).json({ error: 'Error rechazando solicitud' });
        }
        
        if (this.changes === 0) {
          return res.status(404).json({ error: 'Solicitud no encontrada' });
        }
        
        res.json({ message: 'Solicitud rechazada' });
      }
    );
  } catch (error) {
    console.error('Error in reject solicitud:', error);
    res.status(401).json({ error: 'Token inválido' });
  }
});

// Endpoints para reportes/estadísticas
app.get('/api/reportes/estadisticas', (req, res) => {
  try {
    const authHeader = req.headers.authorization;
    if (!authHeader || !authHeader.startsWith('Bearer ')) {
      return res.status(401).json({ error: 'Token no encontrado' });
    }

    const token = authHeader.split(' ')[1];
    const decoded = jwt.verify(token, process.env.JWT_SECRET || 'fallback_secret');
    
    if (decoded.rol === 'C') {
      return res.status(403).json({ error: 'No tienes permisos para ver estadísticas' });
    }

    // Obtener estadísticas
    const queries = [
      'SELECT COUNT(*) as total_usuarios FROM usuarios WHERE activo = 1',
      'SELECT COUNT(*) as solicitudes_pendientes FROM solicitudes_vacaciones WHERE estado = "pendiente"',
      'SELECT COUNT(*) as solicitudes_aprobadas_mes FROM solicitudes_vacaciones WHERE estado = "aprobada" AND date(fecha_aprobacion) >= date("now", "start of month")',
      'SELECT AVG(dias_acumulados) as promedio_dias_acumulados FROM usuarios WHERE activo = 1'
    ];

    let stats = {};
    let completed = 0;

    queries.forEach((query, index) => {
      db.get(query, (err, row) => {
        if (!err && row) {
          Object.assign(stats, row);
        }
        completed++;
        if (completed === queries.length) {
          res.json({
            total_usuarios: stats.total_usuarios || 0,
            solicitudes_pendientes: stats.solicitudes_pendientes || 0,
            solicitudes_aprobadas_mes: stats.solicitudes_aprobadas_mes || 0,
            promedio_dias_acumulados: stats.promedio_dias_acumulados || 0
          });
        }
      });
    });
  } catch (error) {
    console.error('Error in estadisticas:', error);
    res.status(401).json({ error: 'Token inválido' });
  }
});

// API de gestión de usuarios (solo admin/manager)
app.get('/api/usuarios', (req, res) => {
  try {
    const authHeader = req.headers.authorization;
    if (!authHeader || !authHeader.startsWith('Bearer ')) {
      return res.status(401).json({ error: 'Token no encontrado' });
    }

    const token = authHeader.split(' ')[1];
    const decoded = jwt.verify(token, process.env.JWT_SECRET || 'fallback_secret');
    
    if (decoded.rol === 'C') {
      return res.status(403).json({ error: 'No tienes permisos para ver usuarios' });
    }

    db.all(`
      SELECT u.id, u.email, u.nombre, u.apellidos, u.rol, u.departamento_id,
             u.fecha_ingreso, u.dias_acumulados, u.activo, d.nombre as departamento_nombre
      FROM usuarios u
      LEFT JOIN departamentos d ON u.departamento_id = d.id
      ORDER BY u.nombre, u.apellidos
    `, (err, rows) => {
      if (err) {
        console.error('Error fetching usuarios:', err);
        return res.status(500).json({ error: 'Error de base de datos' });
      }
      res.json(rows || []);
    });
  } catch (error) {
    console.error('Error in usuarios endpoint:', error);
    res.status(401).json({ error: 'Token inválido' });
  }
});

app.post('/api/usuarios', (req, res) => {
  try {
    const authHeader = req.headers.authorization;
    if (!authHeader || !authHeader.startsWith('Bearer ')) {
      return res.status(401).json({ error: 'Token no encontrado' });
    }

    const token = authHeader.split(' ')[1];
    const decoded = jwt.verify(token, process.env.JWT_SECRET || 'fallback_secret');
    
    if (decoded.rol !== 'A') {
      return res.status(403).json({ error: 'Solo los administradores pueden crear usuarios' });
    }

    const { email, nombre, apellidos, rol, departamento_id, fecha_ingreso } = req.body;
    
    if (!email || !nombre || !apellidos || !rol || !fecha_ingreso) {
      return res.status(400).json({ error: 'Datos requeridos faltantes' });
    }

    // Contraseña temporal
    const tempPassword = 'temp123';
    const password_hash = bcrypt.hashSync(tempPassword, 10);

    db.run(`
      INSERT INTO usuarios (email, password_hash, nombre, apellidos, rol, departamento_id, fecha_ingreso, dias_acumulados)
      VALUES (?, ?, ?, ?, ?, ?, ?, 25)
    `, [email.toLowerCase(), password_hash, nombre, apellidos, rol, departamento_id, fecha_ingreso], function(err) {
      if (err) {
        console.error('Error creating usuario:', err);
        if (err.message.includes('UNIQUE constraint failed')) {
          return res.status(400).json({ error: 'El email ya está registrado' });
        }
        return res.status(500).json({ error: 'Error creando usuario' });
      }
      
      res.status(201).json({
        message: 'Usuario creado exitosamente',
        id: this.lastID,
        tempPassword: tempPassword
      });
    });
  } catch (error) {
    console.error('Error in create usuario:', error);
    res.status(401).json({ error: 'Token inválido' });
  }
});

app.put('/api/usuarios/:id/toggle', (req, res) => {
  try {
    const authHeader = req.headers.authorization;
    if (!authHeader || !authHeader.startsWith('Bearer ')) {
      return res.status(401).json({ error: 'Token no encontrado' });
    }

    const token = authHeader.split(' ')[1];
    const decoded = jwt.verify(token, process.env.JWT_SECRET || 'fallback_secret');
    
    if (decoded.rol !== 'A') {
      return res.status(403).json({ error: 'Solo los administradores pueden activar/desactivar usuarios' });
    }

    const userId = req.params.id;

    db.run('UPDATE usuarios SET activo = NOT activo WHERE id = ?', [userId], function(err) {
      if (err) {
        console.error('Error toggling usuario:', err);
        return res.status(500).json({ error: 'Error actualizando usuario' });
      }
      
      if (this.changes === 0) {
        return res.status(404).json({ error: 'Usuario no encontrado' });
      }
      
      res.json({ message: 'Estado del usuario actualizado' });
    });
  } catch (error) {
    console.error('Error in toggle usuario:', error);
    res.status(401).json({ error: 'Token inválido' });
  }
});

app.get('/api/departamentos', (req, res) => {
  try {
    const authHeader = req.headers.authorization;
    if (!authHeader || !authHeader.startsWith('Bearer ')) {
      return res.status(401).json({ error: 'Token no encontrado' });
    }

    db.all('SELECT * FROM departamentos WHERE activo = 1 ORDER BY nombre', (err, rows) => {
      if (err) {
        console.error('Error fetching departamentos:', err);
        return res.status(500).json({ error: 'Error de base de datos' });
      }
      res.json(rows || []);
    });
  } catch (error) {
    console.error('Error in departamentos endpoint:', error);
    res.status(401).json({ error: 'Token inválido' });
  }
});

app.get('/health', (req, res) => {
  res.json({ status: 'OK', debug: true });
});

const PORT = 5001; // Usar puerto diferente para debug
app.listen(PORT, () => {
  console.log(`🐛 Debug server running on port ${PORT}`);
});