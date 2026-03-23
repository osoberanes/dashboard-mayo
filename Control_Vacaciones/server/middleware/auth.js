const jwt = require('jsonwebtoken');
const { query } = require('../config/database');

// Middleware para verificar JWT
const authenticateToken = async (req, res, next) => {
  const authHeader = req.headers['authorization'];
  const token = authHeader && authHeader.split(' ')[1]; // Bearer TOKEN

  if (!token) {
    return res.status(401).json({ error: 'Token de acceso requerido' });
  }

  try {
    const decoded = jwt.verify(token, process.env.JWT_SECRET);
    
    // Verificar que el usuario aún existe y está activo
    const result = await query(
      'SELECT id, email, nombre, apellidos, rol, departamento_id, activo FROM usuarios WHERE id = $1 AND activo = true',
      [decoded.userId]
    );

    if (result.rows.length === 0) {
      return res.status(401).json({ error: 'Usuario no válido o inactivo' });
    }

    req.user = result.rows[0];
    next();
  } catch (error) {
    console.error('Error en autenticación:', error);
    return res.status(403).json({ error: 'Token no válido' });
  }
};

// Middleware para verificar roles específicos
const requireRole = (rolesPermitidos) => {
  return (req, res, next) => {
    if (!req.user) {
      return res.status(401).json({ error: 'Usuario no autenticado' });
    }

    if (!rolesPermitidos.includes(req.user.rol)) {
      return res.status(403).json({ 
        error: 'No tienes permisos para acceder a este recurso',
        requiredRoles: rolesPermitidos,
        userRole: req.user.rol
      });
    }

    next();
  };
};

// Middleware específicos por rol
const requireAdmin = requireRole(['A']);
const requireManagerOrAdmin = requireRole(['A', 'B']);
const requireAnyRole = requireRole(['A', 'B', 'C']);

// Middleware para verificar si el usuario puede acceder a un recurso específico
const canAccessUserResource = async (req, res, next) => {
  const targetUserId = parseInt(req.params.userId || req.params.id);
  const currentUser = req.user;

  // Admin puede acceder a todo
  if (currentUser.rol === 'A') {
    return next();
  }

  // Manager puede acceder a usuarios de su departamento
  if (currentUser.rol === 'B') {
    try {
      const result = await query(
        'SELECT departamento_id FROM usuarios WHERE id = $1',
        [targetUserId]
      );

      if (result.rows.length === 0) {
        return res.status(404).json({ error: 'Usuario no encontrado' });
      }

      if (result.rows[0].departamento_id === currentUser.departamento_id) {
        return next();
      }
    } catch (error) {
      console.error('Error verificando acceso:', error);
      return res.status(500).json({ error: 'Error interno del servidor' });
    }
  }

  // Usuario solo puede acceder a sus propios recursos
  if (currentUser.id === targetUserId) {
    return next();
  }

  return res.status(403).json({ 
    error: 'No tienes permisos para acceder a este recurso' 
  });
};

module.exports = {
  authenticateToken,
  requireRole,
  requireAdmin,
  requireManagerOrAdmin,
  requireAnyRole,
  canAccessUserResource
};