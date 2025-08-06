const express = require('express');
const router = express.Router();
const adminController = require('../controllers/adminController');
const authenticateToken = require('../middleware/authMiddleware');

// --- Dashboard stats for cards ---
router.get('/dashboard-stats', authenticateToken, adminController.getDashboardStats);

// --- Recent complaints for table ---
router.get('/recent-complaints', authenticateToken, adminController.getRecentComplaints);

// --- Complaints ---
// List/filter/search all complaints
router.get('/complaints', authenticateToken, adminController.getComplaints);
// Get full complaint details including comments/history
router.get('/complaints/:id', authenticateToken, adminController.getComplaintById);
// Change complaint status
router.patch('/complaints/:id/status', authenticateToken, adminController.updateComplaintStatus);
// Assign/unassign complaint to staff
router.patch('/complaints/:id/assign', authenticateToken, adminController.assignComplaint);
// Add admin comment to complaint
router.post('/complaints/:id/comment', authenticateToken, adminController.addAdminComment);
// Delete a complaint
router.delete('/complaints/:id', authenticateToken, adminController.deleteComplaint);

// --- Users ---
// List users, with search/role filter
router.get('/users', authenticateToken, adminController.getAllUsers);
// Update staff (user) status
router.patch('/users/:id/status', authenticateToken, adminController.updateStaffStatus);
// Delete user (staff or student)
router.delete('/users/:id', authenticateToken, adminController.deleteUser);

// --- Staff for assignment dropdown ---
router.get('/authorized-staff', authenticateToken, adminController.getAuthorizedStaff);

// --- Statistics ---
// General statistics summary
router.get('/statistics', authenticateToken, adminController.getStatistics);
// Longest open complaints
router.get('/statistics/longest-open', authenticateToken, adminController.getLongestOpenComplaints);
// Recently closed complaints
router.get('/statistics/recently-closed', authenticateToken, adminController.getRecentlyClosedComplaints);
// Staff assignment stats
router.get('/statistics/staff-assignment', authenticateToken, adminController.getStaffAssignmentStats);

module.exports = router;
