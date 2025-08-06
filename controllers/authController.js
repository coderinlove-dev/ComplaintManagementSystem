const bcrypt = require('bcrypt');
const jwt = require('jsonwebtoken');
const pool = require('../config/db');

// ========== REGISTER USER OR STAFF ==========
exports.registerUser = async (req, res) => {
  try {
    const {
      first_name,
      last_name,
      email,
      password,
      role,
      roll_number,
      branch
    } = req.body;
    const name = `${first_name} ${last_name}`;

    // 🔍 Debug log to check what role was received from frontend
console.log('Received role from frontend:', role);

    // Find role_id for the provided role
    const [roleRows] = await pool.query('SELECT id FROM roles WHERE name = ?', [role]);
    if (!roleRows.length) return res.status(400).json({ message: 'Invalid role selection.' });

    const role_id = roleRows[0].id;

    // Check if user already exists
    const [userRows] = await pool.query('SELECT * FROM users WHERE email = ?', [email]);
    if (userRows.length) return res.status(409).json({ message: 'Email already registered. Please log in.' });

    // Hash password
    const hashedPassword = await bcrypt.hash(password, 10);

    // Staff require admin approval; students are auto-approved
    let is_approved = true;
    if (role === 'staff') is_approved = false;

    // INSERT user and get inserted user ID
    const [insertResult] = await pool.query(
      `INSERT INTO users
        (name, first_name, last_name, email, password, role_id, is_approved, roll_number, branch)
      VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)`,
      [name, first_name, last_name, email, hashedPassword, role_id, is_approved, roll_number, branch]
    );

    const newUserId = insertResult.insertId;

    if (role === 'staff') {
      // Staff: do NOT generate token. Wait for approval.
      res.status(201).json({ message: 'Staff registration submitted! Await admin approval.' });
    } else if (role === 'student') {
      // Student: Generate JWT and return user info.
      const token = jwt.sign(
        { id: newUserId, role: role },
        process.env.JWT_SECRET,
        { expiresIn: '1d' }
      );
      // Prepare basic user profile to return
      const userProfile = {
        id: newUserId,
        email,
        role,
        first_name,
        last_name,
        roll_number,
        branch
      };
      res.status(201).json({
        message: 'Registration successful!',
        token,
        user: userProfile
      });
    } else {
      // Unexpected role
      res.status(400).json({ message: 'Invalid role specified.' });
    }
  } catch (err) {
    res.status(500).json({ message: 'Registration failed.', error: err.message });
  }
};


// ========== LOGIN USER, STAFF, OR ADMIN ==========
exports.loginUser = async (req, res) => {
  const { email, password } = req.body;
  try {
    const [rows] = await pool.query(
      'SELECT users.*, roles.name as role FROM users JOIN roles ON users.role_id = roles.id WHERE email = ?',
      [email]
    );
    if (!rows.length) {
      return res.status(404).json({ message: 'No account with this email. Please register.' });
    }

    const user = rows[0];

    // If staff and not approved
    if (user.role === 'staff' && !user.is_approved) {
      return res.status(403).json({ message: 'Staff account is pending admin approval.' });
    }

    const match = await bcrypt.compare(password, user.password);
    if (!match) {
      return res.status(401).json({ message: 'Incorrect password.' });
    }

    // Successful login: generate token and return user info
    const token = jwt.sign(
      { id: user.id, role: user.role },
      process.env.JWT_SECRET,
      { expiresIn: '1d' }
    );

    res.json({
      token,
      user: {
        id: user.id,
        email: user.email,
        role: user.role,
        first_name: user.first_name,
        last_name: user.last_name,
        roll_number: user.roll_number,
        branch: user.branch
        // add more fields here if needed
      }
    });
  } catch (err) {
    res.status(500).json({ message: 'Login failed', error: err.message });
  }
};
