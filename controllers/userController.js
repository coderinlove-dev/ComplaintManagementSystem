// controllers/userController.js
const pool = require('../config/db');

exports.getUserProfile = async (req, res) => {
  try {
    const userId = req.user.id; // req.user provided by auth middleware
    const [rows] = await pool.query('SELECT name AS username, email, first_name, last_name, college, roll_number, branch FROM users WHERE id = ?', [userId]);
    if (!rows.length) {
      return res.status(404).json({ message: "No user found" });
    }
    res.json(rows[0]);
  } catch (err) {
    res.status(500).json({ message: "Error loading profile", error: err.message });
  }
};
