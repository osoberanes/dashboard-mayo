const express = require('express');
const router = express.Router();
const { authenticateToken, requireAdmin, requireManagerOrAdmin } = require('../middleware/auth');
const { query } = require('../config/database');

// Todas las rutas requieren autenticación
router.use(authenticateToken);

// Crear nueva solicitud
router.post('/', async (req, res) => {
  try {
    const { fecha_inicio, fecha_fin, dias_solicitados, motivo } = req.body;
    const usuario_id = req.user.id;

    if (!fecha_inicio || !fecha_fin || !dias_solicitados) {
      return res.status(400).json({ 
        error: 'Fecha de inicio, fecha de fin y días solicitados son requeridos' 
      });
    }

    // Verificar que las fechas sean válidas
    const inicio = new Date(fecha_inicio);
    const fin = new Date(fecha_fin);
    
    if (fin < inicio) {
      return res.status(400).json({ 
        error: 'La fecha de fin no puede ser anterior a la fecha de inicio' 
      });
    }

    const result = await query(
      `INSERT INTO solicitudes_vacaciones (usuario_id, fecha_inicio, fecha_fin, dias_solicitados, motivo)
       VALUES ($1, $2, $3, $4, $5)
       RETURNING id, usuario_id, fecha_inicio, fecha_fin, dias_solicitados, estado, created_at`,
      [usuario_id, fecha_inicio, fecha_fin, dias_solicitados, motivo]
    );

    res.status(201).json({
      message: 'Solicitud creada exitosamente',
      solicitud: result.rows[0]
    });

  } catch (error) {
    console.error('Error creando solicitud:', error);
    
    // Manejar errores específicos de validación de triggers
    if (error.message.includes('no pueden terminar en viernes')) {
      return res.status(400).json({ error: 'Las vacaciones no pueden terminar en viernes' });
    }
    if (error.message.includes('usuario espejo')) {
      return res.status(400).json({ error: 'Conflicto: tu usuario espejo tiene vacaciones en el mismo período' });
    }
    if (error.message.includes('departamento')) {
      return res.status(400).json({ error: 'Conflicto: otro usuario del departamento tiene vacaciones en el mismo período' });
    }
    if (error.message.includes('días disponibles')) {
      return res.status(400).json({ error: 'Los días solicitados exceden tus días disponibles' });
    }
    if (error.message.includes('actividades')) {
      return res.status(400).json({ error: 'Tienes actividades asignadas de fin de semana en este período' });
    }
    
    res.status(500).json({ error: 'Error interno del servidor' });
  }
});

// Obtener solicitudes (filtradas por rol)
router.get('/', async (req, res) => {
  try {
    const { estado, usuario_id, departamento_id, fecha_inicio, fecha_fin } = req.query;
    
    let queryText;
    let queryParams = [];
    let paramIndex = 1;

    if (req.user.rol === 'A') {
      // Admin ve todas las solicitudes
      queryText = `
        SELECT sv.*, u.nombre || ' ' || u.apellidos as usuario_nombre, 
               u.email, d.nombre as departamento_nombre
        FROM solicitudes_vacaciones sv
        JOIN usuarios u ON sv.usuario_id = u.id
        LEFT JOIN departamentos d ON u.departamento_id = d.id
        WHERE 1=1
      `;
    } else if (req.user.rol === 'B') {
      // Manager ve solicitudes de su departamento
      queryText = `
        SELECT sv.*, u.nombre || ' ' || u.apellidos as usuario_nombre, 
               u.email, d.nombre as departamento_nombre
        FROM solicitudes_vacaciones sv
        JOIN usuarios u ON sv.usuario_id = u.id
        LEFT JOIN departamentos d ON u.departamento_id = d.id
        WHERE u.departamento_id = $${paramIndex}
      `;
      queryParams.push(req.user.departamento_id);
      paramIndex++;
    } else {
      // User solo ve sus solicitudes
      queryText = `
        SELECT sv.*, u.nombre || ' ' || u.apellidos as usuario_nombre, 
               u.email, d.nombre as departamento_nombre
        FROM solicitudes_vacaciones sv
        JOIN usuarios u ON sv.usuario_id = u.id
        LEFT JOIN departamentos d ON u.departamento_id = d.id
        WHERE sv.usuario_id = $${paramIndex}
      `;
      queryParams.push(req.user.id);
      paramIndex++;
    }

    // Filtros adicionales
    if (estado) {
      queryText += ` AND sv.estado = $${paramIndex}`;
      queryParams.push(estado);
      paramIndex++;
    }

    if (usuario_id && req.user.rol !== 'C') {
      queryText += ` AND sv.usuario_id = $${paramIndex}`;
      queryParams.push(usuario_id);
      paramIndex++;
    }

    if (fecha_inicio) {
      queryText += ` AND sv.fecha_inicio >= $${paramIndex}`;
      queryParams.push(fecha_inicio);
      paramIndex++;
    }

    if (fecha_fin) {
      queryText += ` AND sv.fecha_fin <= $${paramIndex}`;
      queryParams.push(fecha_fin);
      paramIndex++;
    }

    queryText += ' ORDER BY sv.created_at DESC';

    const result = await query(queryText, queryParams);
    res.json(result.rows);

  } catch (error) {
    console.error('Error obteniendo solicitudes:', error);
    res.status(500).json({ error: 'Error interno del servidor' });
  }
});

// Obtener solicitud específica
router.get('/:id', async (req, res) => {
  try {
    const solicitudId = req.params.id;
    
    const result = await query(
      `SELECT sv.*, u.nombre || ' ' || u.apellidos as usuario_nombre, 
              u.email, d.nombre as departamento_nombre,
              ua.nombre || ' ' || ua.apellidos as aprobado_por_nombre
       FROM solicitudes_vacaciones sv
       JOIN usuarios u ON sv.usuario_id = u.id
       LEFT JOIN departamentos d ON u.departamento_id = d.id
       LEFT JOIN usuarios ua ON sv.aprobado_por = ua.id
       WHERE sv.id = $1`,
      [solicitudId]
    );

    if (result.rows.length === 0) {
      return res.status(404).json({ error: 'Solicitud no encontrada' });
    }

    const solicitud = result.rows[0];

    // Verificar permisos de acceso
    if (req.user.rol === 'C' && solicitud.usuario_id !== req.user.id) {
      return res.status(403).json({ error: 'No tienes permisos para ver esta solicitud' });
    }

    if (req.user.rol === 'B' && solicitud.departamento_id !== req.user.departamento_id) {
      return res.status(403).json({ error: 'No tienes permisos para ver esta solicitud' });
    }

    res.json(solicitud);

  } catch (error) {
    console.error('Error obteniendo solicitud:', error);
    res.status(500).json({ error: 'Error interno del servidor' });
  }
});

// Aprobar/rechazar solicitud (solo admin)
router.patch('/:id/status', requireAdmin, async (req, res) => {
  try {
    const { estado, comentarios_admin } = req.body;
    const solicitudId = req.params.id;

    if (!['aprobada', 'rechazada'].includes(estado)) {
      return res.status(400).json({ error: 'Estado inválido. Debe ser "aprobada" o "rechazada"' });
    }

    const result = await query(
      `UPDATE solicitudes_vacaciones 
       SET estado = $1, aprobado_por = $2, fecha_aprobacion = CURRENT_TIMESTAMP, comentarios_admin = $3
       WHERE id = $4
       RETURNING *`,
      [estado, req.user.id, comentarios_admin, solicitudId]
    );

    if (result.rows.length === 0) {
      return res.status(404).json({ error: 'Solicitud no encontrada' });
    }

    res.json({
      message: `Solicitud ${estado} exitosamente`,
      solicitud: result.rows[0]
    });

  } catch (error) {
    console.error('Error actualizando estado de solicitud:', error);
    res.status(500).json({ error: 'Error interno del servidor' });
  }
});

// Cancelar solicitud (solo el usuario propietario y si está pendiente)
router.delete('/:id', async (req, res) => {
  try {
    const solicitudId = req.params.id;

    // Verificar que la solicitud existe y pertenece al usuario
    const checkResult = await query(
      'SELECT estado, usuario_id FROM solicitudes_vacaciones WHERE id = $1',
      [solicitudId]
    );

    if (checkResult.rows.length === 0) {
      return res.status(404).json({ error: 'Solicitud no encontrada' });
    }

    const solicitud = checkResult.rows[0];

    if (solicitud.usuario_id !== req.user.id && req.user.rol !== 'A') {
      return res.status(403).json({ error: 'No tienes permisos para cancelar esta solicitud' });
    }

    if (solicitud.estado !== 'pendiente') {
      return res.status(400).json({ error: 'Solo se pueden cancelar solicitudes pendientes' });
    }

    const result = await query(
      'UPDATE solicitudes_vacaciones SET estado = $1 WHERE id = $2 RETURNING *',
      ['cancelada', solicitudId]
    );

    res.json({
      message: 'Solicitud cancelada exitosamente',
      solicitud: result.rows[0]
    });

  } catch (error) {
    console.error('Error cancelando solicitud:', error);
    res.status(500).json({ error: 'Error interno del servidor' });
  }
});

module.exports = router;