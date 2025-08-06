const pool = require('../config/db');

// Dashboard stats for admin cards
exports.getDashboardStats = async (req, res) => {
  try {
    const [usersRes] = await pool.query("SELECT COUNT(*) AS totalUsers FROM users");
    const [complaintsRes] = await pool.query("SELECT COUNT(*) AS totalComplaints FROM complaints");
    const [solvedRes] = await pool.query("SELECT COUNT(*) AS solvedComplaints FROM complaints WHERE status = 'Solved'");
    const [todayRes] = await pool.query(`
      SELECT COUNT(*) AS newComplaints FROM complaints
      WHERE DATE(created_at) = CURDATE()
    `);

    res.json({
      totalUsers: usersRes[0].totalUsers,
      totalComplaints: complaintsRes[0].totalComplaints,
      solvedComplaints: solvedRes[0].solvedComplaints,
      newComplaints: todayRes[0].newComplaints,
    });
  } catch (err) {
    res.status(500).json({ message: 'Error fetching dashboard stats', error: err.message });
  }
};

// Recent 10 complaints for table
exports.getRecentComplaints = async (req, res) => {
  try {
    const [rows] = await pool.query(`
      SELECT c.id, u.first_name, u.last_name, c.subject, c.created_at, c.status
      FROM complaints c
      JOIN users u ON c.user_id = u.id
      ORDER BY c.created_at DESC
      LIMIT 10
    `);
    const complaints = rows.map((row, idx) => ({
      number: idx + 1,
      user: `${row.first_name} ${row.last_name}`,
      subject: row.subject,
      date: row.created_at,
      status: row.status,
      id: row.id
    }));
    res.json(complaints);
  } catch (err) {
    res.status(500).json({ message: "Error fetching recent complaints", error: err.message });
  }
};

// Get full info for a single complaint (for modal/view)
exports.getComplaintDetails = async (req, res) => {
  try {
    const { id } = req.params;
    const [rows] = await pool.query(
      `SELECT c.id, u.first_name, u.last_name, c.subject, c.type, c.description, c.status, c.created_at, c.updated_at
      FROM complaints c
      JOIN users u ON c.user_id = u.id
      WHERE c.id = ?`,
      [id]
    );
    if (!rows.length) return res.status(404).json({ message: 'Complaint not found' });
    const row = rows[0];
    res.json({
      id: row.id,
      user: `${row.first_name} ${row.last_name}`,
      subject: row.subject,
      type: row.type,
      description: row.description,
      status: row.status,
      created_at: row.created_at,
      updated_at: row.updated_at
    });
  } catch (err) {
    res.status(500).json({ message: 'Error fetching complaint details', error: err.message });
  }
};


exports.getAllUsers = async (req, res) => {
  try {
    const { search = "", role = "" } = req.query;
    let sql = `
      SELECT 
        u.id, 
        CONCAT(COALESCE(u.first_name, ''), ' ', COALESCE(u.last_name, '')) AS name, 
        u.email, 
        r.name AS role,
        CASE 
          WHEN LOWER(r.name) = 'staff' THEN COALESCE(u.staff_status, 'Pending')
          ELSE 'N/A'
        END AS status
      FROM users u
      JOIN roles r ON u.role_id = r.id
      WHERE 1=1
    `;
    const params = [];
    if (search) {
      sql += ` AND (u.first_name LIKE ? OR u.last_name LIKE ? OR u.email LIKE ?)`;
      params.push(`%${search}%`, `%${search}%`, `%${search}%`);
    }
    if (role) {
      sql += ` AND LOWER(r.name) = ?`;
      params.push(role.toLowerCase());
    }
    sql += ` ORDER BY u.id ASC`;
    const [users] = await pool.query(sql, params);
    res.json(users);
  } catch (err) {
    console.error("getAllUsers error:", err);
    res.status(500).json({ message: "Server error" });
  }
};



// Authorize/Reject/Pending update for staff
exports.updateStaffStatus = async (req, res) => {
  try {
    const { id } = req.params;
    const { status } = req.body;
    if (!["Pending", "Authorized", "Rejected"].includes(status)) {
      return res.status(400).json({ message: "Invalid status" });
    }
    const [result] = await pool.query(
      `UPDATE users SET staff_status = ? WHERE id = ? AND role = 'Staff'`,
      [status, id]
    );
    if (result.affectedRows === 0) {
      return res.status(404).json({ message: "Staff member not found" });
    }
    res.json({ message: "Status updated", id, status });
  } catch (err) {
    res.status(500).json({ message: 'Error updating staff status', error: err.message });
  }
};

// Delete any user (staff or student)
exports.deleteUser = async (req, res) => {
  try {
    const { id } = req.params;
    const [result] = await pool.query(`DELETE FROM users WHERE id = ?`, [id]);
    if (result.affectedRows === 0) {
      return res.status(404).json({ message: "User not found" });
    }
    res.json({ message: "User deleted", id });
  } catch (err) {
    res.status(500).json({ message: 'Error deleting user', error: err.message });
  }
};

// Fetch complaints with search/filter/query options
exports.getComplaints = async (req, res) => {
  try {
    const { search = "", role = "", type = "", status = "" } = req.query;
    let sql = `
      SELECT c.id, c.subject, c.type, c.status, c.description,
            c.created_at, c.updated_at, c.assigned_to,
            u.first_name, u.last_name, u.role AS user_role,
            au.first_name AS assigned_first, au.last_name AS assigned_last
      FROM complaints c
      JOIN users u ON c.user_id = u.id
      LEFT JOIN users au ON c.assigned_to = au.id
      WHERE 1=1
    `;
    const params = [];
    if (search) {
      sql += ` AND (u.first_name LIKE ? OR u.last_name LIKE ? OR c.subject LIKE ? OR c.id LIKE ?)`;
      params.push(`%${search}%`, `%${search}%`, `%${search}%`, `%${search}%`);
    }
    if (role) {
      sql += ` AND u.role = ?`;
      params.push(role);
    }
    if (type) {
      sql += ` AND c.type = ?`;
      params.push(type);
    }
    if (status) {
      sql += ` AND c.status = ?`;
      params.push(status);
    }
    sql += " ORDER BY c.created_at DESC";
    const [rows] = await pool.query(sql, params);
    const complaints = rows.map(r => ({
      id: r.id,
      user: `${r.first_name} ${r.last_name}`,
      role: r.user_role,
      type: r.type,
      subject: r.subject,
      status: r.status,
      submitted: r.created_at,
      updated: r.updated_at,
      assignedTo: r.assigned_to ? `${r.assigned_first} ${r.assigned_last}` : "",
    }));
    res.json(complaints);
  } catch (err) {
    res.status(500).json({ message: 'Error fetching complaints', error: err.message });
  }
};

// Get ONE complaint's full details (with comments/history/etc)
exports.getComplaintById = async (req, res) => {
  try {
    const { id } = req.params;
    const [rows] = await pool.query(`
      SELECT c.*, u.first_name, u.last_name, u.role AS user_role,
        au.first_name AS assigned_first, au.last_name AS assigned_last
      FROM complaints c
      JOIN users u ON c.user_id = u.id
      LEFT JOIN users au ON c.assigned_to = au.id
      WHERE c.id = ?
    `, [id]);
    if (!rows.length) return res.status(404).json({ message: "Complaint not found" });
    const c = rows[0];
    const [comments] = await pool.query(`
      SELECT ac.id, ac.comment, ac.created_at, a.first_name, a.last_name
      FROM admin_comments ac
      JOIN users a ON ac.admin_id = a.id
      WHERE ac.complaint_id = ?
      ORDER BY ac.created_at ASC
    `, [id]);
    res.json({
      id: c.id,
      user: `${c.first_name} ${c.last_name}`,
      role: c.user_role,
      subject: c.subject,
      description: c.description,
      type: c.type,
      status: c.status,
      submitted: c.created_at,
      updated: c.updated_at,
      assignedTo: c.assigned_to ? `${c.assigned_first} ${c.assigned_last}` : "",
      comments: comments.map(co => ({
        id: co.id,
        user: `${co.first_name} ${co.last_name}`,
        date: co.created_at,
        msg: co.comment
      })),
    });
  } catch (err) {
    res.status(500).json({ message: 'Error fetching complaint', error: err.message });
  }
};

// Change status (any value allowed: Pending, In Progress, Solved, etc)
exports.updateComplaintStatus = async (req, res) => {
  try {
    const { id } = req.params;
    const { status } = req.body;
    const [result] = await pool.query(
      `UPDATE complaints SET status = ?, updated_at = NOW() WHERE id = ?`,
      [status, id]
    );
    if (result.affectedRows === 0) return res.status(404).json({ message: "Complaint not found" });
    res.json({ message: "Status updated", id, status });
  } catch (err) {
    res.status(500).json({ message: 'Error updating status', error: err.message });
  }
};

// Assign complaint to staff (by staff ID or null to unassign)
exports.assignComplaint = async (req, res) => {
  try {
    const { id } = req.params;
    const { staff_id } = req.body;
    const [result] = await pool.query(
      `UPDATE complaints SET assigned_to = ?, updated_at = NOW() WHERE id = ?`,
      [staff_id || null, id]
    );
    if (result.affectedRows === 0) return res.status(404).json({ message: "Complaint not found" });
    res.json({ message: "Assigned", id, staff_id });
  } catch (err) {
    res.status(500).json({ message: 'Error assigning complaint', error: err.message });
  }
};

// Add admin comment to complaint
exports.addAdminComment = async (req, res) => {
  try {
    const { id } = req.params; // complaint ID
    const { comment } = req.body;
    const adminId = req.user && req.user.id; // from auth middleware
    if (!comment || !comment.trim()) {
      return res.status(400).json({ message: "Empty comment" });
    }
    if (!adminId) {
      return res.status(401).json({ message: "Unauthorized: Admin ID missing" });
    }
    await pool.query(
      `INSERT INTO admin_comments (complaint_id, admin_id, comment, created_at)
       VALUES (?, ?, ?, NOW())`,
      [id, adminId, comment]
    );
    res.json({ message: "Comment added" });
  } catch (err) {
    res.status(500).json({ message: 'Error adding comment', error: err.message });
  }
};

// Delete complaint fully
exports.deleteComplaint = async (req, res) => {
  try {
    const { id } = req.params;
    const [result] = await pool.query(`DELETE FROM complaints WHERE id = ?`, [id]);
    if (result.affectedRows === 0)
      return res.status(404).json({ message: "Complaint not found" });
    res.json({ message: "Complaint deleted", id });
  } catch (err) {
    res.status(500).json({ message: 'Error deleting complaint', error: err.message });
  }
};

// Get list of authorized staff (for "assign" dropdown)
exports.getAuthorizedStaff = async (req, res) => {
  try {
    const [rows] = await pool.query(
      "SELECT id, CONCAT(first_name, ' ', last_name) AS name FROM users WHERE role = 'Staff' AND staff_status = 'Authorized' ORDER BY first_name"
    );
    res.json(rows);
  } catch (err) {
    res.status(500).json({ message: "Error fetching staff list", error: err.message });
  }
};

// --- Statistics Summary for Cards & Breakdown ---
exports.getStatistics = async (req, res) => {
  try {
    const [complaintsRes] = await pool.query("SELECT COUNT(*) AS totalComplaints FROM complaints");
    const [pendingRes] = await pool.query("SELECT COUNT(*) AS pending FROM complaints WHERE status = 'Pending'");
    const [inProgressRes] = await pool.query("SELECT COUNT(*) AS inProgress FROM complaints WHERE status = 'In Progress'");
    const [solvedRes] = await pool.query("SELECT COUNT(*) AS solved FROM complaints WHERE status = 'Solved'");
    const [rejectedRes] = await pool.query("SELECT COUNT(*) AS rejected FROM complaints WHERE status = 'Rejected'");
    const [unassignedRes] = await pool.query("SELECT COUNT(*) AS unassigned FROM complaints WHERE assigned_to IS NULL");
    const [avgResolutionRes] = await pool.query(`
      SELECT AVG(DATEDIFF(updated_at, created_at)) AS avgResolutionDays
      FROM complaints
      WHERE status = 'Solved'
    `);
    const [byType] = await pool.query(`
      SELECT type, COUNT(*) AS count
      FROM complaints
      GROUP BY type
    `);
    const [byRole] = await pool.query(`
      SELECT u.role AS role, COUNT(*) AS count
      FROM complaints c
      JOIN users u ON c.user_id = u.id
      GROUP BY u.role
    `);

    res.json({
      totalComplaints: complaintsRes[0].totalComplaints || 0,
      pending: pendingRes[0].pending || 0,
      inProgress: inProgressRes[0].inProgress || 0,
      solved: solvedRes[0].solved || 0,
      rejected: rejectedRes[0].rejected || 0,
      unassigned: unassignedRes[0].unassigned || 0,
      avgResolutionDays: avgResolutionRes[0].avgResolutionDays ? Number(avgResolutionRes[0].avgResolutionDays).toFixed(2) : 0,
      byType: byType.map(r => ({ type: r.type, count: r.count })),
      byRole: byRole.map(r => ({ role: r.role, count: r.count }))
    });
  } catch (err) {
    res.status(500).json({ message: "Error fetching statistics", error: err.message });
  }
};

// --- Longest open complaints for the main table ---
exports.getLongestOpenComplaints = async (req, res) => {
  try {
    const { search = "", status = "", role = "" } = req.query;
    let sql = `
      SELECT c.id, c.subject, c.status, c.created_at, c.assigned_to,
            u.first_name, u.last_name, u.role AS user_role,
            a.first_name AS assigned_first, a.last_name AS assigned_last
      FROM complaints c
      JOIN users u ON c.user_id = u.id
      LEFT JOIN users a ON c.assigned_to = a.id
      WHERE c.status != 'Solved'
    `;
    const params = [];
    if (search) {
      sql += " AND (c.subject LIKE ? OR u.first_name LIKE ? OR u.last_name LIKE ? OR c.id LIKE ?)";
      params.push(`%${search}%`, `%${search}%`, `%${search}%`, `%${search}%`);
    }
    if (status) { sql += " AND c.status = ?"; params.push(status); }
    if (role) { sql += " AND u.role = ?"; params.push(role); }
    sql += " ORDER BY c.created_at ASC LIMIT 15";
    const [rows] = await pool.query(sql, params);
    const now = new Date();
    const data = rows.map((r, i) => ({
      idx: i + 1,
      subject: r.subject,
      status: r.status,
      user: `${r.first_name} ${r.last_name}`,
      role: r.user_role,
      daysOpen: Math.round((now - new Date(r.created_at)) / (1000 * 60 * 60 * 24)),
      assignedTo: r.assigned_to ? `${r.assigned_first} ${r.assigned_last}` : ""
    }));
    res.json(data);
  } catch (err) {
    res.status(500).json({ message: "Error fetching longest open complaints", error: err.message });
  }
};

// --- Recently closed complaints table ---
exports.getRecentlyClosedComplaints = async (req, res) => {
  try {
    const [rows] = await pool.query(`
      SELECT c.subject, u.first_name, u.last_name, u.role AS user_role, c.updated_at, a.first_name AS assigned_first, a.last_name AS assigned_last
      FROM complaints c
      JOIN users u ON c.user_id = u.id
      LEFT JOIN users a ON c.assigned_to = a.id
      WHERE c.status = 'Solved'
      ORDER BY c.updated_at DESC LIMIT 10
    `);
    const data = rows.map((r, i) => ({
      idx: i + 1,
      subject: r.subject,
      user: `${r.first_name} ${r.last_name}`,
      role: r.user_role,
      closed: r.updated_at,
      assignedTo: r.assigned_first ? `${r.assigned_first} ${r.assigned_last}` : ""
    }));
    res.json(data);
  } catch (err) {
    res.status(500).json({ message: "Error fetching closed complaints", error: err.message });
  }
};

// --- By staff assignment table ---
exports.getStaffAssignmentStats = async (req, res) => {
  try {
    const [rows] = await pool.query(`
      SELECT u.id, CONCAT(u.first_name, ' ', u.last_name) AS staff, COUNT(c.id) AS assigned
      FROM users u
      LEFT JOIN complaints c ON u.id = c.assigned_to
      WHERE u.role = 'Staff'
      GROUP BY u.id
      ORDER BY assigned DESC, staff ASC
      LIMIT 20
    `);
    const data = rows.map((x, i) => ({ idx: i + 1, staff: x.staff, assigned: x.assigned }));
    res.json(data);
  } catch (err) {
    res.status(500).json({ message: "Error fetching staff assignment stats", error: err.message });
  }
};
