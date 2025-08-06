const express = require('express');
const router = express.Router();
const staffController = require('../controllers/staffController');
const authenticateToken = require('../middleware/authMiddleware');

// Staff profile (for sidebar/header)
router.get('/profile', authenticateToken, staffController.getProfile);

// Stats (numbers, for dashboard + chart)
router.get('/complaints/stats', authenticateToken, staffController.getComplaintStats);

// List all complaints, with search and filter from query params
router.get('/complaints', authenticateToken, staffController.allComplaints);

// Update complaint status
router.post('/complaints/:id/status', authenticateToken, staffController.updateComplaintStatus);

// All solved complaints for table
router.get('/complaints/solved', authenticateToken, staffController.getAllSolvedComplaints);

module.exports = router;
