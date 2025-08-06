const pool = require('../config/db');
const bcrypt = require('bcrypt');

// Helper: get a setting by key
async function getSetting(key) {
  const [[row]] = await pool.query('SELECT setting_value FROM admin_settings WHERE setting_key = ?', [key]);
  return row ? row.setting_value : null;
}

// Helper: set a setting key to value
async function setSetting(key, value) {
  await pool.query(
    `INSERT INTO admin_settings (setting_key, setting_value)
     VALUES (?, ?) ON DUPLICATE KEY UPDATE setting_value = VALUES(setting_value)`,
    [key, value]
  );
}

// --- 1. Change admin password and update session timeout ---
exports.changeAdminPassword = async (req, res) => {
  try {
    const { adminId } = req.user; // Ensure only admin can make this request, from JWT
    const { password, sessionTimeout } = req.body;
    if (password && password.length < 6) return res.status(400).json({ message: "Password too short" });

    if (password) {
      const hash = await bcrypt.hash(password, 10);
      await pool.query('UPDATE users SET password = ? WHERE id = ?', [hash, adminId]);
    }

    if (sessionTimeout) await setSetting('session_timeout', sessionTimeout);

    res.json({ message: "Security settings updated" });
  } catch (err) {
    res.status(500).json({ message: "Error updating security", error: err.message });
  }
};

// --- 2. User management preferences (approval, default role, password policy) ---
exports.saveUserPrefs = async (req, res) => {
  try {
    const { staffApprovalNeeded, defaultUserRole, pwPolicy } = req.body;
    await setSetting('staff_approval_needed', !!staffApprovalNeeded ? "1" : "0");
    await setSetting('default_user_role', defaultUserRole);
    await setSetting('password_policy', pwPolicy);
    res.json({ message: "User preferences saved." });
  } catch (err) {
    res.status(500).json({ message: "Error saving user prefs", error: err.message });
  }
};

// --- 3. Complaint system settings ---
exports.saveComplaintSys = async (req, res) => {
  try {
    const { defaultStatus, categories, slaDays, attachLimitMb } = req.body;
    await setSetting('default_complaint_status', defaultStatus);
    await setSetting('complaint_categories', categories); // comma separated
    await setSetting('sla_days', slaDays);
    await setSetting('attachment_limit_mb', attachLimitMb);
    res.json({ message: "Complaint system settings saved." });
  } catch (err) {
    res.status(500).json({ message: "Error saving complaint system settings", error: err.message });
  }
};

// --- 4. Customization & branding ---
exports.saveBrand = async (req, res) => {
  try {
    const { systemName, colorTheme } = req.body;
    // Optionally handle file upload for logo
    await setSetting('system_name', systemName);
    await setSetting('color_theme', colorTheme);
    res.json({ message: "Branding settings saved." });
  } catch (err) {
    res.status(500).json({ message: "Error saving branding", error: err.message });
  }
};

// --- 5. Data & Support policy ---
exports.saveDataPolicy = async (req, res) => {
  try {
    const { retentionDays, privacyLevel } = req.body;
    await setSetting('data_retention_days', retentionDays);
    await setSetting('privacy_level', privacyLevel);
    res.json({ message: "Data policy saved." });
  } catch (err) {
    res.status(500).json({ message: "Error saving data policy", error: err.message });
  }
};

// Fetch all settings at once
exports.getAllSettings = async (req, res) => {
  try {
    const [rows] = await pool.query('SELECT setting_key, setting_value FROM admin_settings');
    const settings = {};
    rows.forEach(row => { settings[row.setting_key] = row.setting_value; });
    res.json(settings);
  } catch (err) {
    res.status(500).json({ message: "Error fetching settings", error: err.message });
  }
};
