// routes/userRoutes.js
const express = require('express');
const router = express.Router();
const userController = require('../controllers/userController');
const authenticateToken = require('../middleware/authMiddleware'); // your JWT checker

router.get('/me', authenticateToken, userController.getUserProfile);

module.exports = router;
