const express = require('express');
const router = express.Router();
const authController = require('../controllers/authController');
const { authenticateToken, requireAdmin } = require('../middleware/auth');

// Rutas públicas
router.post('/login', authController.login);

// Rutas protegidas
router.use(authenticateToken); // Aplicar autenticación a todas las rutas siguientes

// Perfil y verificación
router.get('/profile', authController.getProfile);
router.get('/verify', authController.verifyToken);
router.post('/change-password', authController.changePassword);

// Solo administradores
router.post('/create-user', requireAdmin, authController.createUser);

module.exports = router;