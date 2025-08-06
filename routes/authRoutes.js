const express = require('express');
const router = express.Router();
const authController = require('../controllers/authController');

router.post('/login', authController.loginUser);

module.exports = router;

// Register endpoint
router.post('/register', authController.registerUser);
// Login endpoint
router.post('/login', authController.loginUser);

module.exports = router;
