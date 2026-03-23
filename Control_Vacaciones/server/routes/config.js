const express = require('express');
const router = express.Router();
const { authenticateToken, requireAdmin } = require('../middleware/auth');
const { query } = require('../config/database');

// Todas las rutas requieren autenticación
router.use(authenticateToken);

// Obtener configuración (todos los usuarios autenticados)
router.get('/', async (req, res) => {
  try {
    const result = await query(
      'SELECT clave, valor, descripcion FROM configuracion_sistema ORDER BY clave'
    );
    
    // Convertir a objeto para facilitar uso en frontend
    const config = {};
    result.rows.forEach(row => {
      config[row.clave] = {
        valor: row.valor,
        descripcion: row.descripcion
      };
    });

    res.json(config);
  } catch (error) {
    console.error('Error obteniendo configuración:', error);
    res.status(500).json({ error: 'Error interno del servidor' });
  }
});

// Actualizar configuración (solo admin)
router.put('/', requireAdmin, async (req, res) => {
  try {
    const configuraciones = req.body;
    
    if (!configuraciones || typeof configuraciones !== 'object') {
      return res.status(400).json({ error: 'Configuraciones inválidas' });
    }

    const updates = [];
    for (const [clave, valor] of Object.entries(configuraciones)) {
      updates.push(
        query(
          'UPDATE configuracion_sistema SET valor = $1 WHERE clave = $2',
          [valor, clave]
        )
      );
    }

    await Promise.all(updates);

    res.json({ message: 'Configuración actualizada exitosamente' });
  } catch (error) {
    console.error('Error actualizando configuración:', error);
    res.status(500).json({ error: 'Error interno del servidor' });
  }
});

// Obtener días festivos
router.get('/dias-festivos', async (req, res) => {
  try {
    const { year } = req.query;
    
    let queryText = 'SELECT * FROM dias_festivos';
    let queryParams = [];

    if (year) {
      queryText += ' WHERE EXTRACT(YEAR FROM fecha) = $1';
      queryParams.push(year);
    }

    queryText += ' ORDER BY fecha';

    const result = await query(queryText, queryParams);
    res.json(result.rows);
  } catch (error) {
    console.error('Error obteniendo días festivos:', error);
    res.status(500).json({ error: 'Error interno del servidor' });
  }
});

// Agregar día festivo (solo admin)
router.post('/dias-festivos', requireAdmin, async (req, res) => {
  try {
    const { fecha, nombre, descripcion } = req.body;

    if (!fecha || !nombre) {
      return res.status(400).json({ error: 'Fecha y nombre son requeridos' });
    }

    const result = await query(
      'INSERT INTO dias_festivos (fecha, nombre, descripcion) VALUES ($1, $2, $3) RETURNING *',
      [fecha, nombre, descripcion]
    );

    res.status(201).json({
      message: 'Día festivo agregado exitosamente',
      diaFestivo: result.rows[0]
    });
  } catch (error) {
    console.error('Error agregando día festivo:', error);
    if (error.code === '23505') { // Unique violation
      return res.status(400).json({ error: 'Ya existe un día festivo en esa fecha' });
    }
    res.status(500).json({ error: 'Error interno del servidor' });
  }
});

// Eliminar día festivo (solo admin)
router.delete('/dias-festivos/:id', requireAdmin, async (req, res) => {
  try {
    const result = await query(
      'DELETE FROM dias_festivos WHERE id = $1 RETURNING *',
      [req.params.id]
    );

    if (result.rows.length === 0) {
      return res.status(404).json({ error: 'Día festivo no encontrado' });
    }

    res.json({ message: 'Día festivo eliminado exitosamente' });
  } catch (error) {
    console.error('Error eliminando día festivo:', error);
    res.status(500).json({ error: 'Error interno del servidor' });
  }
});

module.exports = router;