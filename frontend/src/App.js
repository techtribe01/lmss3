import React, { useState, useEffect, createContext, useContext } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate, useNavigate, useLocation, Link } from 'react-router-dom';
import './App.css';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL || 'http://localhost:8001';

// Auth Context
const AuthContext = createContext(null);

const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const token = localStorage.getItem('token');
    const storedUser = localStorage.getItem('user');
    if (token && storedUser) {
      setUser(JSON.parse(storedUser));
    }
    setLoading(false);
  }, []);

  const login = (token, userData) => {
    localStorage.setItem('token', token);
    localStorage.setItem('user', JSON.stringify(userData));
    setUser(userData);
  };

  const logout = () => {
    localStorage.removeItem('token');
    localStorage.removeItem('user');
    setUser(null);
  };

  return (
    <AuthContext.Provider value={{ user, login, logout, loading }}>
      {children}
    </AuthContext.Provider>
  );
};

const useAuth = () => useContext(AuthContext);

// Protected Route Component
const ProtectedRoute = ({ children, allowedRoles }) => {
  const { user, loading } = useAuth();

  if (loading) {
    return <div className="loading-screen">Loading...</div>;
  }

  if (!user) {
    return <Navigate to="/login" />;
  }

  if (allowedRoles && !allowedRoles.includes(user.role)) {
    return <Navigate to="/" />;
  }

  return children;
};

// Login Page
const LoginPage = () => {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const navigate = useNavigate();
  const { login } = useAuth();

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');

    try {
      const response = await fetch(`${BACKEND_URL}/api/auth/login`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ username, password })
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.detail || 'Login failed');
      }

      login(data.access_token, data.user);
      
      // Navigate based on role
      if (data.user.role === 'admin') navigate('/admin');
      else if (data.user.role === 'mentor') navigate('/mentor');
      else if (data.user.role === 'student') navigate('/student');
    } catch (err) {
      setError(err.message);
    }
  };

  return (
    <div className="auth-container">
      <div className="auth-card">
        <h1 className="auth-title">Welcome Back</h1>
        <p className="auth-subtitle">Sign in to your LMS account</p>
        
        <form onSubmit={handleSubmit} className="auth-form">
          {error && <div className="error-message">{error}</div>}
          
          <div className="form-group">
            <label>Username</label>
            <input
              type="text"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              required
              placeholder="Enter your username"
            />
          </div>

          <div className="form-group">
            <label>Password</label>
            <input
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
              placeholder="Enter your password"
            />
          </div>

          <button type="submit" className="auth-button">Sign In</button>
        </form>

        <p className="auth-footer">
          Don't have an account? <Link to="/register">Sign up</Link>
        </p>
      </div>
    </div>
  );
};

// Register Page
const RegisterPage = () => {
  const [formData, setFormData] = useState({
    username: '',
    email: '',
    password: '',
    full_name: '',
    role: 'student'
  });
  const [error, setError] = useState('');
  const navigate = useNavigate();
  const { login } = useAuth();

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');

    try {
      const response = await fetch(`${BACKEND_URL}/api/auth/register`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(formData)
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.detail || 'Registration failed');
      }

      login(data.access_token, data.user);
      
      // Navigate based on role
      if (data.user.role === 'admin') navigate('/admin');
      else if (data.user.role === 'mentor') navigate('/mentor');
      else if (data.user.role === 'student') navigate('/student');
    } catch (err) {
      setError(err.message);
    }
  };

  return (
    <div className="auth-container">
      <div className="auth-card">
        <h1 className="auth-title">Create Account</h1>
        <p className="auth-subtitle">Join our learning platform</p>
        
        <form onSubmit={handleSubmit} className="auth-form">
          {error && <div className="error-message">{error}</div>}
          
          <div className="form-group">
            <label>Full Name</label>
            <input
              type="text"
              value={formData.full_name}
              onChange={(e) => setFormData({...formData, full_name: e.target.value})}
              required
              placeholder="Enter your full name"
            />
          </div>

          <div className="form-group">
            <label>Username</label>
            <input
              type="text"
              value={formData.username}
              onChange={(e) => setFormData({...formData, username: e.target.value})}
              required
              placeholder="Choose a username"
            />
          </div>

          <div className="form-group">
            <label>Email</label>
            <input
              type="email"
              value={formData.email}
              onChange={(e) => setFormData({...formData, email: e.target.value})}
              required
              placeholder="Enter your email"
            />
          </div>

          <div className="form-group">
            <label>Password</label>
            <input
              type="password"
              value={formData.password}
              onChange={(e) => setFormData({...formData, password: e.target.value})}
              required
              placeholder="Create a password"
            />
          </div>

          <div className="form-group">
            <label>Role</label>
            <select
              value={formData.role}
              onChange={(e) => setFormData({...formData, role: e.target.value})}
              required
            >
              <option value="student">Student</option>
              <option value="mentor">Mentor</option>
              <option value="admin">Admin</option>
            </select>
          </div>

          <button type="submit" className="auth-button">Create Account</button>
        </form>

        <p className="auth-footer">
          Already have an account? <Link to="/login">Sign in</Link>
        </p>
      </div>
    </div>
  );
};

// Sidebar Component
const Sidebar = ({ isOpen, toggleSidebar, menuItems, role }) => {
  const navigate = useNavigate();
  const location = useLocation();
  const { logout } = useAuth();

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  return (
    <>
      <div className={`sidebar ${isOpen ? 'open' : 'closed'}`}>
        <div className="sidebar-header">
          <h2 className="sidebar-logo">{role.toUpperCase()} Portal</h2>
        </div>
        
        <nav className="sidebar-nav">
          {menuItems.map((item, index) => (
            <Link
              key={index}
              to={item.path}
              className={`sidebar-item ${location.pathname === item.path ? 'active' : ''}`}
            >
              <span className="sidebar-icon">{item.icon}</span>
              <span className="sidebar-text">{item.label}</span>
            </Link>
          ))}
        </nav>

        <div className="sidebar-footer">
          <button onClick={handleLogout} className="logout-button">
            <span className="sidebar-icon">⎋</span>
            <span className="sidebar-text">Logout</span>
          </button>
        </div>
      </div>
      
      {isOpen && <div className="sidebar-overlay" onClick={toggleSidebar}></div>}
    </>
  );
};

// Dashboard Layout
const DashboardLayout = ({ children, menuItems, role }) => {
  const [sidebarOpen, setSidebarOpen] = useState(true);
  const { user } = useAuth();

  return (
    <div className="dashboard-container">
      <Sidebar 
        isOpen={sidebarOpen} 
        toggleSidebar={() => setSidebarOpen(!sidebarOpen)}
        menuItems={menuItems}
        role={role}
      />
      
      <div className={`main-content ${sidebarOpen ? 'sidebar-open' : 'sidebar-closed'}`}>
        <header className="top-header">
          <button onClick={() => setSidebarOpen(!sidebarOpen)} className="menu-toggle">
            ☰
          </button>
          <div className="user-info">
            <span className="user-name">{user?.full_name}</span>
            <span className="user-role">{user?.role}</span>
          </div>
        </header>
        
        <main className="page-content">
          {children}
        </main>
      </div>
    </div>
  );
};

// Coming Soon Component
const ComingSoon = ({ title, description }) => (
  <div className="coming-soon">
    <div className="coming-soon-content">
      <h1 className="page-title">{title}</h1>
      {description && <p className="page-description">{description}</p>}
      <div className="placeholder-box">
        <span className="placeholder-icon">🚧</span>
        <h2>Coming Soon</h2>
        <p>This feature is under development</p>
      </div>
    </div>
  </div>
);

// Admin Pages
const AdminDashboard = () => <ComingSoon title="Admin Dashboard" description="Overview of system metrics and activities" />;
const CoursesManagement = () => <ComingSoon title="Courses Management" description="Create and manage courses" />;
const MentorManagement = () => <ComingSoon title="Mentor Management" description="Manage mentor accounts and assignments" />;
const StudentManagement = () => <ComingSoon title="Student Management" description="Manage student accounts and enrollments" />;
const ReportsOverview = () => <ComingSoon title="Reports Overview" description="View system-wide reports and analytics" />;
const CourseApproval = () => <ComingSoon title="Course Approval" description="Review and approve course submissions" />;
const BatchDownloads = () => <ComingSoon title="Batch Video Downloads" description="Download course videos in batches" />;
const MockInterviews = () => <ComingSoon title="Mock Interview Appointments" description="Schedule and manage mock interviews" />;
const AssignmentsGrading = () => <ComingSoon title="Assignments Grading" description="Review and grade student assignments" />;
const FeeAlerts = () => <ComingSoon title="Fee Reminder Alerts" description="Manage fee payment reminders" />;

// Mentor Pages
const MentorDashboard = () => <ComingSoon title="Mentor Dashboard" description="Your teaching overview and quick actions" />;
const MentorCourses = () => <ComingSoon title="Course List & Edit" description="View and edit your courses" />;
const VideoSessions = () => <ComingSoon title="Video Sessions" description="Zoom/Teams integration for live classes" />;
const TaskAssignment = () => <ComingSoon title="Task Assignment" description="Create and assign tasks to students" />;
const AttendanceManagement = () => <ComingSoon title="Attendance Management" description="Track student attendance" />;
const ProgressTracking = () => <ComingSoon title="Progress Tracking" description="Monitor student progress" />;
const MaterialsUpload = () => <ComingSoon title="Materials Upload" description="Upload course materials and resources" />;
const CertificateGeneration = () => <ComingSong title="Certificate Generation" description="Generate certificates for students" />;

// Student Pages
const StudentDashboard = () => <ComingSoon title="Student Dashboard" description="Your learning journey at a glance" />;
const CoursesList = () => <ComingSoon title="Courses List" description="Browse available courses" />;
const RegisteredCourses = () => <ComingSoon title="Registered Courses" description="Your enrolled courses" />;
const TaskSubmission = () => <ComingSoon title="Task Submission" description="Submit assignments and tasks" />;
const AttendanceView = () => <ComingSoon title="Attendance View" description="View your attendance records" />;
const Certificates = () => <ComingSoon title="Certificates" description="Your earned certificates" />;

// Security Page
const SecurityProctoring = () => <ComingSoon title="Security & Proctoring Setup" description="Configure security and proctoring settings" />;

// Admin Menu Items
const adminMenuItems = [
  { path: '/admin', label: 'Dashboard', icon: '📊' },
  { path: '/admin/courses', label: 'Courses Management', icon: '📚' },
  { path: '/admin/mentors', label: 'Mentor Management', icon: '👨‍🏫' },
  { path: '/admin/students', label: 'Student Management', icon: '👨‍🎓' },
  { path: '/admin/reports', label: 'Reports Overview', icon: '📈' },
  { path: '/admin/course-approval', label: 'Course Approval', icon: '✅' },
  { path: '/admin/batch-downloads', label: 'Batch Downloads', icon: '⬇️' },
  { path: '/admin/mock-interviews', label: 'Mock Interviews', icon: '🎤' },
  { path: '/admin/assignments', label: 'Assignments Grading', icon: '📝' },
  { path: '/admin/fee-alerts', label: 'Fee Alerts', icon: '💰' },
  { path: '/admin/security', label: 'Security & Proctoring', icon: '🔒' }
];

// Mentor Menu Items
const mentorMenuItems = [
  { path: '/mentor', label: 'Dashboard', icon: '📊' },
  { path: '/mentor/courses', label: 'Course List & Edit', icon: '📚' },
  { path: '/mentor/video-sessions', label: 'Video Sessions', icon: '🎥' },
  { path: '/mentor/tasks', label: 'Task Assignment', icon: '📋' },
  { path: '/mentor/attendance', label: 'Attendance Management', icon: '✓' },
  { path: '/mentor/progress', label: 'Progress Tracking', icon: '📈' },
  { path: '/mentor/materials', label: 'Materials Upload', icon: '📤' },
  { path: '/mentor/certificates', label: 'Certificate Generation', icon: '🏆' }
];

// Student Menu Items
const studentMenuItems = [
  { path: '/student', label: 'Dashboard', icon: '📊' },
  { path: '/student/courses', label: 'Courses List', icon: '📚' },
  { path: '/student/registered', label: 'Registered Courses', icon: '✓' },
  { path: '/student/tasks', label: 'Task Submission', icon: '📝' },
  { path: '/student/attendance', label: 'Attendance View', icon: '📅' },
  { path: '/student/certificates', label: 'Certificates', icon: '🏆' }
];

function App() {
  return (
    <Router>
      <AuthProvider>
        <Routes>
          {/* Public Routes */}
          <Route path="/login" element={<LoginPage />} />
          <Route path="/register" element={<RegisterPage />} />
          
          {/* Admin Routes */}
          <Route path="/admin/*" element={
            <ProtectedRoute allowedRoles={['admin']}>
              <DashboardLayout menuItems={adminMenuItems} role="admin">
                <Routes>
                  <Route path="/" element={<AdminDashboard />} />
                  <Route path="/courses" element={<CoursesManagement />} />
                  <Route path="/mentors" element={<MentorManagement />} />
                  <Route path="/students" element={<StudentManagement />} />
                  <Route path="/reports" element={<ReportsOverview />} />
                  <Route path="/course-approval" element={<CourseApproval />} />
                  <Route path="/batch-downloads" element={<BatchDownloads />} />
                  <Route path="/mock-interviews" element={<MockInterviews />} />
                  <Route path="/assignments" element={<AssignmentsGrading />} />
                  <Route path="/fee-alerts" element={<FeeAlerts />} />
                  <Route path="/security" element={<SecurityProctoring />} />
                </Routes>
              </DashboardLayout>
            </ProtectedRoute>
          } />
          
          {/* Mentor Routes */}
          <Route path="/mentor/*" element={
            <ProtectedRoute allowedRoles={['mentor']}>
              <DashboardLayout menuItems={mentorMenuItems} role="mentor">
                <Routes>
                  <Route path="/" element={<MentorDashboard />} />
                  <Route path="/courses" element={<MentorCourses />} />
                  <Route path="/video-sessions" element={<VideoSessions />} />
                  <Route path="/tasks" element={<TaskAssignment />} />
                  <Route path="/attendance" element={<AttendanceManagement />} />
                  <Route path="/progress" element={<ProgressTracking />} />
                  <Route path="/materials" element={<MaterialsUpload />} />
                  <Route path="/certificates" element={<CertificateGeneration />} />
                </Routes>
              </DashboardLayout>
            </ProtectedRoute>
          } />
          
          {/* Student Routes */}
          <Route path="/student/*" element={
            <ProtectedRoute allowedRoles={['student']}>
              <DashboardLayout menuItems={studentMenuItems} role="student">
                <Routes>
                  <Route path="/" element={<StudentDashboard />} />
                  <Route path="/courses" element={<CoursesList />} />
                  <Route path="/registered" element={<RegisteredCourses />} />
                  <Route path="/tasks" element={<TaskSubmission />} />
                  <Route path="/attendance" element={<AttendanceView />} />
                  <Route path="/certificates" element={<Certificates />} />
                </Routes>
              </DashboardLayout>
            </ProtectedRoute>
          } />
          
          {/* Default Route */}
          <Route path="/" element={<Navigate to="/login" />} />
        </Routes>
      </AuthProvider>
    </Router>
  );
}

export default App;