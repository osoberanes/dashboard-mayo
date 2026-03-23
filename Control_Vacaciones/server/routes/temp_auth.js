const express = require('express');
const router = express.Router();

// Ruta temporal para evitar errores
router.get('/test', (req, res) => {
  res.json({ message: 'Auth route working' });
});

module.exports = router;