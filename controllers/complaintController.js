const pool = require('../config/db');
const path = require('path');
const fs = require('fs');

// Handle file uploads if you want; use multer for real projects
exports.addComplaint = async (req, res) => {
  try {
    const user_id = req.user.id; // req.user set by authenticateToken middleware
    const { subject, type, description } = req.body;
    let attachment = null;

    // if using file upload middleware like multer:
    if (req.file) {
      attachment = req.file.filename;
    }

    // Insert complaint into DB
    await pool.query(
      `INSERT INTO complaints (user_id, subject, type, description, attachment, status)
       VALUES (?, ?, ?, ?, ?, ?)`,
      [user_id, subject, type, description, attachment, 'Unsolved']
    );

    res.status(201).json({ message: 'Complaint submitted successfully!' });
  } catch (err) {
    res.status(500).json({ message: 'Could not submit complaint', error: err.message });
  }
};
// Get all Unsolved complaints for logged-in user
exports.getUserUnsolvedComplaints = async (req, res) => {
  try {
    const userId = req.user.id; // from JWT middleware

    const [rows] = await pool.query(
      `SELECT c.id, u.first_name, u.last_name, c.subject, c.type, c.description, c.status, c.created_at
       FROM complaints c
       JOIN users u ON c.user_id = u.id
       WHERE c.user_id = ? AND c.status = 'Unsolved'
       ORDER BY c.created_at DESC`,
      [userId]
    );
    res.json(rows.map(row => ({
      id: row.id,
      user: `${row.first_name} ${row.last_name}`,
      subject: row.subject,
      type: row.type,
      issued_date: row.created_at,
      description: row.description,
      status: row.status // 'Unsolved' etc
    })));
  } catch (error) {
    res.status(500).json({ message: "Unable to fetch complaints", error: error.message });
  }
};

// Get all Solved complaints for the logged-in user
exports.getUserSolvedComplaints = async (req, res) => {
  try {
    const userId = req.user.id; // Provided by JWT middleware
    const [rows] = await pool.query(
      `SELECT c.id, u.first_name, u.last_name, c.subject, c.type, c.description, c.status, c.created_at
      FROM complaints c
      JOIN users u ON c.user_id = u.id
      WHERE c.user_id = ? AND c.status = 'Solved'
      ORDER BY c.created_at DESC`,
      [userId]
    );
    res.json(rows.map(row => ({
      id: row.id,
      user: `${row.first_name} ${row.last_name}`,
      subject: row.subject,
      type: row.type,
      issued_date: row.created_at,
      description: row.description,
      status: row.status
    })));
  } catch (err) {
    res.status(500).json({ message: "Unable to fetch solved complaints", error: err.message });
  }
};

