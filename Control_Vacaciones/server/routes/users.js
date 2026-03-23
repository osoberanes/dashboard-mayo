const express = require('express');
const router = express.Router();
const { authenticateToken, requireAdmin, requireManagerOrAdmin, canAccessUserResource } = require('../middleware/auth');
const { query } = require('../config/database');

// Todas las rutas requieren autenticación
router.use(authenticateToken);

// Obtener lista de usuarios (Admin: todos, Manager: su departamento, User: solo él)
router.get('/', async (req, res) => {
  try {
    let queryText;
    let queryParams;

    if (req.user.rol === 'A') {
      // Admin ve todos los usuarios
      queryText = `
        SELECT u.id, u.email, u.nombre, u.apellidos, u.rol, u.departamento_id,
               u.fecha_ingreso, u.dias_acumulados, u.activo, d.nombre as departamento_nombre
        FROM usuarios u 
        LEFT JOIN departamentos d ON u.departamento_id = d.id
        ORDER BY u.nombre, u.apellidos
      `;
      queryParams = [];
    } else if (req.user.rol === 'B') {
      // Manager ve usuarios de su departamento
      queryText = `
        SELECT u.id, u.email, u.nombre, u.apellidos, u.rol, u.departamento_id,
               u.fecha_ingreso, u.dias_acumulados, u.activo, d.nombre as departamento_nombre
        FROM usuarios u 
        LEFT JOIN departamentos d ON u.departamento_id = d.id
        WHERE u.departamento_id = $1
        ORDER BY u.nombre, u.apellidos
      `;
      queryParams = [req.user.departamento_id];
    } else {
      // User solo se ve a sí mismo
      queryText = `
        SELECT u.id, u.email, u.nombre, u.apellidos, u.rol, u.departamento_id,
               u.fecha_ingreso, u.dias_acumulados, u.activo, d.nombre as departamento_nombre
        FROM usuarios u 
        LEFT JOIN departamentos d ON u.departamento_id = d.id
        WHERE u.id = $1
      `;
      queryParams = [req.user.id];
    }

    const result = await query(queryText, queryParams);
    res.json(result.rows);

  } catch (error) {
    console.error('Error obteniendo usuarios:', error);
    res.status(500).json({ error: 'Error interno del servidor' });
  }
});

// Obtener usuario específico
router.get('/:id', canAccessUserResource, async (req, res) => {
  try {
    const result = await query(
      `SELECT u.id, u.email, u.nombre, u.apellidos, u.rol, u.departamento_id,
              u.fecha_ingreso, u.dias_acumulados, u.activo, d.nombre as departamento_nombre,
              ue.nombre || ' ' || ue.apellidos as usuario_espejo_nombre
       FROM usuarios u 
       LEFT JOIN departamentos d ON u.departamento_id = d.id
       LEFT JOIN usuarios ue ON u.usuario_espejo_id = ue.id
       WHERE u.id = $1`,
      [req.params.id]
    );

    if (result.rows.length === 0) {
      return res.status(404).json({ error: 'Usuario no encontrado' });
    }

    res.json(result.rows[0]);

  } catch (error) {
    console.error('Error obteniendo usuario:', error);
    res.status(500).json({ error: 'Error interno del servidor' });
  }
});

// Actualizar usuario (solo admin)
router.put('/:id', requireAdmin, async (req, res) => {
  try {
    const { nombre, apellidos, rol, departamento_id, usuario_espejo_id, activo } = req.body;
    const userId = req.params.id;

    const result = await query(
      `UPDATE usuarios 
       SET nombre = $1, apellidos = $2, rol = $3, departamento_id = $4, 
           usuario_espejo_id = $5, activo = $6
       WHERE id = $7
       RETURNING id, email, nombre, apellidos, rol, departamento_id, activo`,
      [nombre, apellidos, rol, departamento_id, usuario_espejo_id, activo, userId]
    );

    if (result.rows.length === 0) {
      return res.status(404).json({ error: 'Usuario no encontrado' });
    }

    res.json({
      message: 'Usuario actualizado exitosamente',
      user: result.rows[0]
    });

  } catch (error) {
    console.error('Error actualizando usuario:', error);
    res.status(500).json({ error: 'Error interno del servidor' });
  }
});

// Obtener resumen de días de vacaciones
router.get('/:id/vacation-summary', canAccessUserResource, async (req, res) => {
  try {
    const result = await query(
      `SELECT 
         u.dias_acumulados,
         COALESCE(SUM(CASE WHEN sv.estado = 'aprobada' THEN sv.dias_solicitados ELSE 0 END), 0) as dias_usados,
         (u.dias_acumulados - COALESCE(SUM(CASE WHEN sv.estado = 'aprobada' THEN sv.dias_solicitados ELSE 0 END), 0)) as dias_disponibles,
         COUNT(CASE WHEN sv.estado = 'pendiente' THEN 1 END) as solicitudes_pendientes
       FROM usuarios u
       LEFT JOIN solicitudes_vacaciones sv ON u.id = sv.usuario_id
       WHERE u.id = $1
       GROUP BY u.id, u.dias_acumulados`,
      [req.params.id]
    );

    if (result.rows.length === 0) {
      return res.status(404).json({ error: 'Usuario no encontrado' });
    }

    res.json(result.rows[0]);

  } catch (error) {
    console.error('Error obteniendo resumen de vacaciones:', error);
    res.status(500).json({ error: 'Error interno del servidor' });
  }
});

module.exports = router;