const bcrypt = require('bcryptjs');
const jwt = require('jsonwebtoken');
const { query } = require('../config/database');

// Función para generar JWT
const generateToken = (userId, email, rol) => {
  return jwt.sign(
    { userId, email, rol },
    process.env.JWT_SECRET,
    { expiresIn: process.env.JWT_EXPIRES_IN || '24h' }
  );
};

// Login de usuario
const login = (req, res) => {
  const { email, password } = req.body;

  if (!email || !password) {
    return res.status(400).json({ 
      error: 'Email y contraseña son requeridos' 
    });
  }

  console.log('📥 Login request for:', email);

  // Usar SQLite directamente para evitar problemas de query conversion
  const sqlite3 = require('sqlite3').verbose();
  const path = require('path');
  const dbPath = path.join(__dirname, '../../database.sqlite');
  const db = new sqlite3.Database(dbPath);

  db.get('SELECT * FROM usuarios WHERE email = ?', [email.toLowerCase()], async (err, user) => {
    if (err) {
      console.error('❌ Database error:', err);
      db.close();
      return res.status(500).json({ error: 'Error de base de datos' });
    }

    if (!user) {
      console.log('❌ User not found');
      db.close();
      return res.status(401).json({ error: 'Credenciales inválidas' });
    }

    if (!user.activo) {
      console.log('❌ User inactive');
      db.close();
      return res.status(401).json({ error: 'Usuario inactivo' });
    }

    try {
      const passwordMatch = await bcrypt.compare(password, user.password_hash);
      
      if (!passwordMatch) {
        console.log('❌ Invalid password');
        db.close();
        return res.status(401).json({ error: 'Credenciales inválidas' });
      }

      // Generar token
      const token = generateToken(user.id, user.email, user.rol);

      console.log('✅ Login successful for:', email);
      db.close();

      res.json({
        message: 'Login exitoso',
        token,
        user: {
          id: user.id,
          email: user.email,
          nombre: user.nombre,
          apellidos: user.apellidos,
          rol: user.rol,
          departamento_id: user.departamento_id,
          departamento_nombre: 'N/A',
          activo: user.activo
        }
      });

    } catch (passwordError) {
      console.error('❌ Password comparison error:', passwordError);
      db.close();
      return res.status(500).json({ error: 'Error verificando contraseña' });
    }
  });
};

// Crear nuevo usuario (solo admin)
const createUser = async (req, res) => {
  try {
    const { 
      email, 
      password, 
      nombre, 
      apellidos, 
      rol, 
      departamento_id, 
      usuario_espejo_id,
      fecha_ingreso 
    } = req.body;

    // Validaciones básicas
    if (!email || !password || !nombre || !apellidos || !rol || !fecha_ingreso) {
      return res.status(400).json({ 
        error: 'Todos los campos obligatorios deben completarse' 
      });
    }

    if (!['A', 'B', 'C'].includes(rol)) {
      return res.status(400).json({ 
        error: 'Rol inválido. Debe ser A, B o C' 
      });
    }

    // Verificar que el email no existe
    const existingUser = await query(
      'SELECT id FROM usuarios WHERE email = $1',
      [email.toLowerCase()]
    );

    if (existingUser.rows.length > 0) {
      return res.status(400).json({ error: 'Email ya está registrado' });
    }

    // Hash de la contraseña
    const saltRounds = 10;
    const password_hash = await bcrypt.hash(password, saltRounds);

    // Crear usuario
    const result = await query(
      `INSERT INTO usuarios (email, password_hash, nombre, apellidos, rol, 
                            departamento_id, usuario_espejo_id, fecha_ingreso)
       VALUES ($1, $2, $3, $4, $5, $6, $7, $8)
       RETURNING id, email, nombre, apellidos, rol, departamento_id, fecha_ingreso`,
      [email.toLowerCase(), password_hash, nombre, apellidos, rol, 
       departamento_id, usuario_espejo_id, fecha_ingreso]
    );

    const newUser = result.rows[0];
    
    // Calcular días acumulados iniciales
    await query(
      'UPDATE usuarios SET dias_acumulados = calcular_dias_acumulados($1) WHERE id = $2',
      [fecha_ingreso, newUser.id]
    );

    res.status(201).json({
      message: 'Usuario creado exitosamente',
      user: newUser
    });

  } catch (error) {
    console.error('Error creando usuario:', error);
    res.status(500).json({ error: 'Error interno del servidor' });
  }
};

// Cambiar contraseña
const changePassword = async (req, res) => {
  try {
    const { currentPassword, newPassword } = req.body;
    const userId = req.user.id;

    if (!currentPassword || !newPassword) {
      return res.status(400).json({ 
        error: 'Contraseña actual y nueva son requeridas' 
      });
    }

    if (newPassword.length < 6) {
      return res.status(400).json({ 
        error: 'La nueva contraseña debe tener al menos 6 caracteres' 
      });
    }

    // Verificar contraseña actual
    const result = await query(
      'SELECT password_hash FROM usuarios WHERE id = $1',
      [userId]
    );

    const user = result.rows[0];
    const passwordMatch = await bcrypt.compare(currentPassword, user.password_hash);
    
    if (!passwordMatch) {
      return res.status(400).json({ error: 'Contraseña actual incorrecta' });
    }

    // Hash de la nueva contraseña
    const saltRounds = 10;
    const newPasswordHash = await bcrypt.hash(newPassword, saltRounds);

    // Actualizar contraseña
    await query(
      'UPDATE usuarios SET password_hash = $1 WHERE id = $2',
      [newPasswordHash, userId]
    );

    res.json({ message: 'Contraseña actualizada exitosamente' });

  } catch (error) {
    console.error('Error cambiando contraseña:', error);
    res.status(500).json({ error: 'Error interno del servidor' });
  }
};

// Obtener perfil del usuario actual
const getProfile = async (req, res) => {
  try {
    const result = await query(
      `SELECT u.id, u.email, u.nombre, u.apellidos, u.rol, u.departamento_id,
              u.fecha_ingreso, u.dias_acumulados, d.nombre as departamento_nombre,
              ue.nombre || ' ' || ue.apellidos as usuario_espejo_nombre
       FROM usuarios u 
       LEFT JOIN departamentos d ON u.departamento_id = d.id
       LEFT JOIN usuarios ue ON u.usuario_espejo_id = ue.id
       WHERE u.id = $1`,
      [req.user.id]
    );

    if (result.rows.length === 0) {
      return res.status(404).json({ error: 'Usuario no encontrado' });
    }

    res.json(result.rows[0]);

  } catch (error) {
    console.error('Error obteniendo perfil:', error);
    res.status(500).json({ error: 'Error interno del servidor' });
  }
};

// Verificar token
const verifyToken = (req, res) => {
  res.json({ 
    valid: true, 
    user: req.user 
  });
};

module.exports = {
  login,
  createUser,
  changePassword,
  getProfile,
  verifyToken
};