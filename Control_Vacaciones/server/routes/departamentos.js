const express = require('express');
const router = express.Router();
const { authenticateToken, requireAdmin } = require('../middleware/auth');
const { query } = require('../config/database');

// Todas las rutas requieren autenticación
router.use(authenticateToken);

// Obtener todos los departamentos
router.get('/', async (req, res) => {
  try {
    const result = await query(
      'SELECT * FROM departamentos WHERE activo = true ORDER BY nombre'
    );
    res.json(result.rows);
  } catch (error) {
    console.error('Error obteniendo departamentos:', error);
    res.status(500).json({ error: 'Error interno del servidor' });
  }
});

// Obtener departamento específico
router.get('/:id', async (req, res) => {
  try {
    const result = await query(
      'SELECT * FROM departamentos WHERE id = $1',
      [req.params.id]
    );

    if (result.rows.length === 0) {
      return res.status(404).json({ error: 'Departamento no encontrado' });
    }

    res.json(result.rows[0]);
  } catch (error) {
    console.error('Error obteniendo departamento:', error);
    res.status(500).json({ error: 'Error interno del servidor' });
  }
});

// Crear departamento (solo admin)
router.post('/', requireAdmin, async (req, res) => {
  try {
    const { nombre, descripcion } = req.body;

    if (!nombre) {
      return res.status(400).json({ error: 'Nombre del departamento es requerido' });
    }

    const result = await query(
      'INSERT INTO departamentos (nombre, descripcion) VALUES ($1, $2) RETURNING *',
      [nombre, descripcion]
    );

    res.status(201).json({
      message: 'Departamento creado exitosamente',
      departamento: result.rows[0]
    });
  } catch (error) {
    console.error('Error creando departamento:', error);
    if (error.code === '23505') { // Unique violation
      return res.status(400).json({ error: 'Ya existe un departamento con ese nombre' });
    }
    res.status(500).json({ error: 'Error interno del servidor' });
  }
});

// Actualizar departamento (solo admin)
router.put('/:id', requireAdmin, async (req, res) => {
  try {
    const { nombre, descripcion, activo } = req.body;

    const result = await query(
      'UPDATE departamentos SET nombre = $1, descripcion = $2, activo = $3 WHERE id = $4 RETURNING *',
      [nombre, descripcion, activo, req.params.id]
    );

    if (result.rows.length === 0) {
      return res.status(404).json({ error: 'Departamento no encontrado' });
    }

    res.json({
      message: 'Departamento actualizado exitosamente',
      departamento: result.rows[0]
    });
  } catch (error) {
    console.error('Error actualizando departamento:', error);
    res.status(500).json({ error: 'Error interno del servidor' });
  }
});

module.exports = router;