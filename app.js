require('dotenv').config();
const express = require('express');
const cors = require('cors');
const userRoutes = require('./routes/userRoutes');
const path = require('path');

const app = express();

// Middleware
app.use(express.json());
app.use(cors());

app.use(express.static(path.join(__dirname, 'public')));

app.use('/api/user', userRoutes);
const complaintRoutes = require('./routes/complaintRoutes');
app.use('/api/complaints', complaintRoutes);
const staffRoutes = require('./routes/staffRoutes');
app.use('/api/staff', staffRoutes);
const adminRoutes = require('./routes/adminRoutes');
app.use('/api/admin', adminRoutes);
const adminSettingsRoutes = require('./routes/adminSettingsRoutes');
app.use('/api/admin/settings', adminSettingsRoutes);

// Routes
const authRoutes = require('./routes/authRoutes');
app.use('/api/auth', authRoutes);

const PORT = process.env.PORT || 5000;
app.listen(PORT, () => console.log(`Server running on port ${PORT}`));
