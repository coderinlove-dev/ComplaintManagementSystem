const pool = require('../config/db');

// Get the current staff user's profile (for sidebar/navbar)
exports.getProfile = async (req, res) => {
  try {
    const staffId = req.user.id;
    const [rows] = await pool.query(
      'SELECT first_name, last_name FROM users WHERE id = ?',
      [staffId]
    );
    if (!rows.length)
      return res.status(404).json({ message: 'Staff not found' });
    res.json({ name: `${rows[0].first_name} ${rows[0].last_name}` });
  } catch (err) {
    res.status(500).json({ message: 'Error fetching staff profile' });
  }
};

// Dashboard statistics and chart data for staff dashboard
exports.getComplaintStats = async (req, res) => {
  try {
    const [[{ total }]] = await pool.query(
      "SELECT COUNT(*) AS total FROM complaints"
    );
    const [[{ unsolved }]] = await pool.query(
      "SELECT COUNT(*) AS unsolved FROM complaints WHERE status = 'Unsolved'"
    );
    const [[{ solved }]] = await pool.query(
      "SELECT COUNT(*) AS solved FROM complaints WHERE status = 'Solved'"
    );
    const [[{ pending }]] = await pool.query(
      "SELECT COUNT(*) AS pending FROM complaints WHERE status = 'Pending'"
    );
    const [byType] = await pool.query(
      `SELECT type, 
        SUM(status='Unsolved') AS unsolved, 
        SUM(status='Pending') AS pending, 
        SUM(status='Solved') AS solved, 
        COUNT(*) as total
      FROM complaints GROUP BY type`
    );

    res.json({ total, unsolved, pending, solved, byType });
  } catch (err) {
    res.status(500).json({ message: 'Error fetching statistics', error: err.message });
  }
};

// List/search/filter all complaints (for allcomplaints.html)
exports.allComplaints = async (req, res) => {
  try {
    const { search = "", type = "" } = req.query;
    let sql = `
      SELECT c.id, c.subject, c.type, c.description, c.status, c.created_at, c.user_id, u.first_name, u.last_name
      FROM complaints c
      JOIN users u ON c.user_id = u.id
      WHERE 1=1
    `;
    const params = [];
    if (search) {
      sql += ` AND (
        u.first_name LIKE ? OR
        u.last_name LIKE ? OR
        c.subject LIKE ? OR
        c.type LIKE ?
      )`;
      params.push(`%${search}%`, `%${search}%`, `%${search}%`, `%${search}%`);
    }
    if (type) {
      sql += ` AND c.type = ?`;
      params.push(type);
    }
    sql += " ORDER BY c.created_at DESC";

    const [rows] = await pool.query(sql, params);
    const complaints = rows.map(row => ({
      id: row.id,
      user: `${row.first_name} ${row.last_name}`,
      subject: row.subject,
      type: row.type,
      issued: row.created_at,
      desc: row.description,
      status: row.status,
    }));
    res.json(complaints);
  } catch (err) {
    res.status(500).json({ message: "Error fetching complaints", error: err.message });
  }
};

// Update/change complaint status (Pending, Solved, Unsolved)
exports.updateComplaintStatus = async (req, res) => {
  try {
    const { id } = req.params;
    const { status } = req.body;
    if (!["Pending", "Solved", "Unsolved"].includes(status)) {
      return res.status(400).json({ message: "Invalid status" });
    }
    const [result] = await pool.query(
      `UPDATE complaints SET status = ? WHERE id = ?`,
      [status, id]
    );
    if (result.affectedRows === 0) {
      return res.status(404).json({ message: "Complaint not found" });
    }
    res.json({ message: "Status updated", id, status });
  } catch (err) {
    res.status(500).json({ message: "Error updating status", error: err.message });
  }
};

// All solved complaints (for staffsolvedcomplaint.html)
exports.getAllSolvedComplaints = async (req, res) => {
  try {
    const [rows] = await pool.query(
      `SELECT c.id, 
              u.first_name, 
              u.last_name,
              c.subject, 
              c.type, 
              c.description, 
              c.status, 
              c.created_at, 
              c.updated_at
        FROM complaints c
        JOIN users u ON c.user_id = u.id
        WHERE c.status = 'Solved'
        ORDER BY c.updated_at DESC`
    );
    const complaints = rows.map(row => ({
      id: row.id,
      user: `${row.first_name} ${row.last_name}`,
      subject: row.subject,
      type: row.type,
      issuedDate: row.created_at,
      solvedDate: row.updated_at,
      description: row.description,
      status: row.status
    }));
    res.json(complaints);
  } catch (err) {
    res.status(500).json({ message: "Error fetching solved complaints", error: err.message });
  }
};
