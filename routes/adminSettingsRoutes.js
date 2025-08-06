const express = require('express');
const router = express.Router();
const adminSettingsController = require('../controllers/adminSettingsController');
const authenticateToken = require('../middleware/authMiddleware'); // Or your admin-only middleware

router.get('/', authenticateToken, adminSettingsController.getAllSettings);

// Each form’s save button should POST/PUT to one of these endpoints:
router.post('/security', authenticateToken, adminSettingsController.changeAdminPassword);
router.post('/userprefs', authenticateToken, adminSettingsController.saveUserPrefs);
router.post('/complaintsys', authenticateToken, adminSettingsController.saveComplaintSys);
router.post('/brand', authenticateToken, adminSettingsController.saveBrand);
router.post('/datapolicy', authenticateToken, adminSettingsController.saveDataPolicy);

module.exports = router;
