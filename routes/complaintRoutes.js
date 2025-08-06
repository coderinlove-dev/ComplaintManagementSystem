const express = require('express');
const router = express.Router();
const complaintController = require('../controllers/complaintController');
const authenticateToken = require('../middleware/authMiddleware');

// For file uploads, add multer here (see below for details)
const multer = require('multer');
const upload = multer({ dest: 'uploads/' });
// POST /api/complaints (protected route)
// New version (with multer)
router.post('/', authenticateToken, upload.single('attachment'), complaintController.addComplaint);

router.get('/unsolved', authenticateToken, complaintController.getUserUnsolvedComplaints);

router.get('/solved', authenticateToken, complaintController.getUserSolvedComplaints);

module.exports = router;