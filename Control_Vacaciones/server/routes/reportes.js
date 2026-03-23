const express = require('express');
const router = express.Router();
const { authenticateToken, requireManagerOrAdmin } = require('../middleware/auth');
const { query } = require('../config/database');

// Todas las rutas requieren autenticación y rol manager o admin
router.use(authenticateToken);
router.use(requireManagerOrAdmin);

// Reporte de usuarios con días disponibles
router.get('/usuarios-dias', async (req, res) => {
  try {
    const result = await query(`
      SELECT * FROM vista_usuarios_dias_disponibles
      ORDER BY departamento, nombre, apellidos
    `);
    res.json(result.rows);
  } catch (error) {
    console.error('Error obteniendo reporte de usuarios:', error);
    res.status(500).json({ error: 'Error interno del servidor' });
  }
});

// Reporte de calendario de vacaciones
router.get('/calendario', async (req, res) => {
  try {
    const { fecha_inicio, fecha_fin, departamento_id } = req.query;
    
    let queryText = 'SELECT * FROM vista_calendario_vacaciones WHERE 1=1';
    let queryParams = [];
    let paramIndex = 1;

    if (fecha_inicio) {
      queryText += ` AND fecha_inicio >= $${paramIndex}`;
      queryParams.push(fecha_inicio);
      paramIndex++;
    }

    if (fecha_fin) {
      queryText += ` AND fecha_fin <= $${paramIndex}`;
      queryParams.push(fecha_fin);
      paramIndex++;
    }

    if (departamento_id) {
      queryText += ` AND departamento = (SELECT nombre FROM departamentos WHERE id = $${paramIndex})`;
      queryParams.push(departamento_id);
      paramIndex++;
    }

    queryText += ' ORDER BY fecha_inicio';

    const result = await query(queryText, queryParams);
    res.json(result.rows);
  } catch (error) {
    console.error('Error obteniendo reporte de calendario:', error);
    res.status(500).json({ error: 'Error interno del servidor' });
  }
});

// Estadísticas generales
router.get('/estadisticas', async (req, res) => {
  try {
    const stats = await Promise.all([
      query('SELECT COUNT(*) as total_usuarios FROM usuarios WHERE activo = true'),
      query('SELECT COUNT(*) as solicitudes_pendientes FROM solicitudes_vacaciones WHERE estado = $1', ['pendiente']),
      query('SELECT COUNT(*) as solicitudes_aprobadas_mes FROM solicitudes_vacaciones WHERE estado = $1 AND EXTRACT(MONTH FROM created_at) = EXTRACT(MONTH FROM CURRENT_DATE)', ['aprobada']),
      query('SELECT AVG(dias_acumulados) as promedio_dias_acumulados FROM usuarios WHERE activo = true'),
      query(`
        SELECT d.nombre, COUNT(u.id) as total_usuarios
        FROM departamentos d
        LEFT JOIN usuarios u ON d.id = u.departamento_id AND u.activo = true
        WHERE d.activo = true
        GROUP BY d.id, d.nombre
        ORDER BY d.nombre
      `)
    ]);

    res.json({
      total_usuarios: parseInt(stats[0].rows[0].total_usuarios),
      solicitudes_pendientes: parseInt(stats[1].rows[0].solicitudes_pendientes),
      solicitudes_aprobadas_mes: parseInt(stats[2].rows[0].solicitudes_aprobadas_mes),
      promedio_dias_acumulados: parseFloat(stats[3].rows[0].promedio_dias_acumulados || 0),
      usuarios_por_departamento: stats[4].rows
    });
  } catch (error) {
    console.error('Error obteniendo estadísticas:', error);
    res.status(500).json({ error: 'Error interno del servidor' });
  }
});

module.exports = router;