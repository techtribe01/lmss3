import React, { useState, useEffect, createContext, useContext } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate, useNavigate, useLocation, Link } from 'react-router-dom';
import { motion, AnimatePresence } from 'framer-motion';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { Sun, Moon, Monitor, User, Mail, Lock, Eye, EyeOff } from 'lucide-react';
import './App.css';
import * as mockService from './services/mockService';
import { loginSchema, registerSchema } from './lib/validationSchemas';
import { Input, PasswordInput, Select, Button, FormValidationSummary } from './components/FormComponents';
import { ThemeProvider, useTheme } from './contexts/ThemeContext';
import { ToastProvider, useToast } from './contexts/ToastContext';
import { SkeletonCard, SkeletonTable, SkeletonStat, SkeletonList } from './components/SkeletonLoader';

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
    return (
      <motion.div 
        className="loading-screen"
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        exit={{ opacity: 0 }}
      >
        <div className="loading-spinner"></div>
        <p>Loading...</p>
      </motion.div>
    );
  }

  if (!user) {
    return <Navigate to="/login" replace />;
  }

  if (allowedRoles && !allowedRoles.includes(user.role)) {
    return <Navigate to="/" replace />;
  }

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, y: -20 }}
      transition={{ duration: 0.3 }}
    >
      {children}
    </motion.div>
  );
};

// Reusable Components
const StatCard = ({ icon, label, value, trend, color = 'blue' }) => (
  <div className={`stat-card stat-card-${color}`}>
    <div className="stat-icon">{icon}</div>
    <div className="stat-content">
      <div className="stat-label">{label}</div>
      <div className="stat-value">{value}</div>
      {trend && <div className="stat-trend">{trend}</div>}
    </div>
  </div>
);

const CourseCard = ({ title, instructor, students, progress, image, category, duration, level }) => (
  <motion.div 
    className="course-card"
    initial={{ opacity: 0, y: 20 }}
    animate={{ opacity: 1, y: 0 }}
    whileHover={{ y: -5, transition: { duration: 0.2 } }}
    whileTap={{ scale: 0.98 }}
  >
    <div className="course-image" style={{ background: image }}>
      {category && <span className="course-badge">{category}</span>}
    </div>
    <div className="course-body">
      <h3 className="course-title">{title}</h3>
      <p className="course-instructor">👨‍🏫 {instructor}</p>
      <div className="course-meta">
        {duration && <span className="meta-item">⏱️ {duration}</span>}
        {level && <span className="meta-item">📊 {level}</span>}
        {students && <span className="meta-item">👥 {students} students</span>}
      </div>
      {progress !== undefined && (
        <div className="progress-container">
          <div className="progress-bar">
            <motion.div 
              className="progress-fill" 
              initial={{ width: 0 }}
              animate={{ width: `${progress}%` }}
              transition={{ duration: 1, ease: "easeOut" }}
            ></motion.div>
          </div>
          <span className="progress-text">{progress}% Complete</span>
        </div>
      )}
    </div>
  </motion.div>
);

const DataTable = ({ columns, data, actions }) => (
  <div className="data-table-container">
    <table className="data-table">
      <thead>
        <tr>
          {columns.map((col, idx) => (
            <th key={idx}>{col}</th>
          ))}
          {actions && <th>Actions</th>}
        </tr>
      </thead>
      <tbody>
        {data.map((row, idx) => (
          <tr key={idx}>
            {row.map((cell, cellIdx) => (
              <td key={cellIdx}>{cell}</td>
            ))}
            {actions && (
              <td>
                <div className="table-actions">
                  {actions.map((action, actIdx) => (
                    <button key={actIdx} className={`btn-icon ${action.variant || ''}`} title={action.label}>
                      {action.icon}
                    </button>
                  ))}
                </div>
              </td>
            )}
          </tr>
        ))}
      </tbody>
    </table>
  </div>
);

const Modal = ({ isOpen, onClose, title, children }) => {
  return (
    <AnimatePresence>
      {isOpen && (
        <motion.div 
          className="modal-overlay" 
          onClick={onClose}
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          exit={{ opacity: 0 }}
          transition={{ duration: 0.2 }}
        >
          <motion.div 
            className="modal-content" 
            onClick={(e) => e.stopPropagation()}
            initial={{ scale: 0.9, opacity: 0, y: 20 }}
            animate={{ scale: 1, opacity: 1, y: 0 }}
            exit={{ scale: 0.9, opacity: 0, y: 20 }}
            transition={{ duration: 0.3 }}
          >
            <div className="modal-header">
              <h2>{title}</h2>
              <motion.button 
                className="modal-close" 
                onClick={onClose}
                whileHover={{ scale: 1.1, rotate: 90 }}
                whileTap={{ scale: 0.9 }}
              >
                ✕
              </motion.button>
            </div>
            <div className="modal-body">
              {children}
            </div>
          </motion.div>
        </motion.div>
      )}
    </AnimatePresence>
  );
};

const SearchFilter = ({ onSearch, filters }) => (
  <div className="search-filter-bar">
    <div className="search-box">
      <span className="search-icon">🔍</span>
      <input type="text" placeholder="Search..." onChange={(e) => onSearch && onSearch(e.target.value)} />
    </div>
    {filters && (
      <div className="filter-group">
        {filters.map((filter, idx) => (
          <select key={idx} className="filter-select">
            <option>{filter.label}</option>
            {filter.options.map((opt, optIdx) => (
              <option key={optIdx} value={opt}>{opt}</option>
            ))}
          </select>
        ))}
      </div>
    )}
  </div>
);

// Login Page
const LoginPage = () => {
  const navigate = useNavigate();
  const { login } = useAuth();
  const { success, error: showError } = useToast();

  const {
    register,
    handleSubmit,
    formState: { errors, isSubmitting, isValid },
    setError,
    clearErrors
  } = useForm({
    resolver: zodResolver(loginSchema),
    mode: 'onChange'
  });

  const onSubmit = async (data) => {
    clearErrors();

    try {
      const response = await fetch(`${BACKEND_URL}/api/auth/login`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(data)
      });

      const result = await response.json();

      if (!response.ok) {
        throw new Error(result.detail || 'Login failed');
      }

      // Show success message
      success('Welcome back! Redirecting to your dashboard...');
      
      // Login user
      login(result.access_token, result.user);
      
      // Navigate based on role with delay for better UX
      setTimeout(() => {
        if (result.user.role === 'admin') navigate('/admin');
        else if (result.user.role === 'mentor') navigate('/mentor');
        else if (result.user.role === 'student') navigate('/student');
      }, 500);
    } catch (err) {
      showError(err.message, { title: 'Login Failed' });
      setError('root', { message: err.message });
    }
  };

  return (
    <motion.div 
      className="auth-container"
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      exit={{ opacity: 0 }}
    >
      <motion.div 
        className="auth-card"
        initial={{ scale: 0.9, y: 20 }}
        animate={{ scale: 1, y: 0 }}
        transition={{ duration: 0.4 }}
      >
        <motion.h1 
          className="auth-title"
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.1 }}
        >
          Welcome Back
        </motion.h1>
        <motion.p 
          className="auth-subtitle"
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.2 }}
        >
          Sign in to your LMS account
        </motion.p>
        
        <form onSubmit={handleSubmit(onSubmit)} className="auth-form">
          <FormValidationSummary errors={errors} />
          
          <motion.div 
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.1 }}
          >
            <Input
              {...register('username')}
              label="Username or Email"
              placeholder="Enter your username or email"
              icon={User}
              error={errors.username?.message}
              disabled={isSubmitting}
              required
            />
          </motion.div>

          <motion.div 
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.2 }}
          >
            <PasswordInput
              {...register('password')}
              label="Password"
              placeholder="Enter your password"
              error={errors.password?.message}
              disabled={isSubmitting}
              required
            />
          </motion.div>

          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.3 }}
          >
            <Button
              type="submit"
              variant="primary"
              size="lg"
              isLoading={isSubmitting}
              disabled={!isValid}
              className="w-full"
            >
              {isSubmitting ? 'Signing In...' : 'Sign In'}
            </Button>
          </motion.div>
        </form>

        <motion.p 
          className="auth-footer"
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.4 }}
        >
          Don't have an account? <Link to="/register">Sign up</Link>
        </motion.p>
      </motion.div>
    </motion.div>
  );
};

// Register Page
const RegisterPage = () => {
  const navigate = useNavigate();
  const { login } = useAuth();
  const { success, error: showError } = useToast();

  const {
    register,
    handleSubmit,
    watch,
    formState: { errors, isSubmitting, isValid },
    setError,
    clearErrors
  } = useForm({
    resolver: zodResolver(registerSchema),
    mode: 'onChange'
  });

  const watchPassword = watch('password', '');

  const roleOptions = [
    { value: 'student', label: 'Student' },
    { value: 'mentor', label: 'Mentor' },
    { value: 'admin', label: 'Admin' }
  ];

  const onSubmit = async (data) => {
    clearErrors();

    try {
      // Remove confirmPassword from data before sending
      const { confirmPassword, ...submitData } = data;

      const response = await fetch(`${BACKEND_URL}/api/auth/register`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(submitData)
      });

      const result = await response.json();

      if (!response.ok) {
        throw new Error(result.detail || 'Registration failed');
      }

      // Show success message
      success('Account created successfully! Redirecting to your dashboard...');
      
      // Login user
      login(result.access_token, result.user);
      
      // Navigate based on role with delay for better UX
      setTimeout(() => {
        if (result.user.role === 'admin') navigate('/admin');
        else if (result.user.role === 'mentor') navigate('/mentor');
        else if (result.user.role === 'student') navigate('/student');
      }, 500);
    } catch (err) {
      showError(err.message, { title: 'Registration Failed' });
      setError('root', { message: err.message });
    }
  };

  return (
    <motion.div 
      className="auth-container"
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      exit={{ opacity: 0 }}
    >
      <motion.div 
        className="auth-card"
        initial={{ scale: 0.9, y: 20 }}
        animate={{ scale: 1, y: 0 }}
        transition={{ duration: 0.4 }}
      >
        <motion.h1 
          className="auth-title"
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.1 }}
        >
          Create Account
        </motion.h1>
        <motion.p 
          className="auth-subtitle"
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.2 }}
        >
          Join our learning platform
        </motion.p>
        
        <form onSubmit={handleSubmit(onSubmit)} className="auth-form">
          <FormValidationSummary errors={errors} />
          
          <motion.div 
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.1 }}
          >
            <Input
              {...register('full_name')}
              label="Full Name"
              placeholder="Enter your full name"
              icon={User}
              error={errors.full_name?.message}
              disabled={isSubmitting}
              required
            />
          </motion.div>

          <div className="form-row">
            <motion.div 
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.2 }}
            >
              <Input
                {...register('username')}
                label="Username"
                placeholder="Choose a username"
                icon={User}
                error={errors.username?.message}
                disabled={isSubmitting}
                hint="3-20 characters, letters, numbers, and underscores only"
                required
              />
            </motion.div>

            <motion.div 
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.25 }}
            >
              <Input
                {...register('email')}
                label="Email"
                type="email"
                placeholder="Enter your email"
                icon={Mail}
                error={errors.email?.message}
                disabled={isSubmitting}
                required
              />
            </motion.div>
          </div>

          <motion.div 
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.3 }}
          >
            <PasswordInput
              {...register('password')}
              label="Password"
              placeholder="Create a strong password"
              error={errors.password?.message}
              disabled={isSubmitting}
              showStrength={true}
              value={watchPassword}
              required
            />
          </motion.div>

          <motion.div 
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.35 }}
          >
            <PasswordInput
              {...register('confirmPassword')}
              label="Confirm Password"
              placeholder="Confirm your password"
              error={errors.confirmPassword?.message}
              disabled={isSubmitting}
              required
            />
          </motion.div>

          <motion.div 
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.4 }}
          >
            <Select
              {...register('role')}
              label="Role"
              options={roleOptions}
              placeholder="Select your role"
              error={errors.role?.message}
              disabled={isSubmitting}
              required
            />
          </motion.div>

          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.45 }}
          >
            <Button
              type="submit"
              variant="primary"
              size="lg"
              isLoading={isSubmitting}
              disabled={!isValid}
              className="w-full"
            >
              {isSubmitting ? 'Creating Account...' : 'Create Account'}
            </Button>
          </motion.div>
        </form>

        <motion.p 
          className="auth-footer"
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.5 }}
        >
          Already have an account? <Link to="/login">Sign in</Link>
        </p>
      </motion.div>
    </motion.div>
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
            <Link key={index} to={item.path} className={`sidebar-item ${location.pathname === item.path ? 'active' : ''}`}>
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
      <Sidebar isOpen={sidebarOpen} toggleSidebar={() => setSidebarOpen(!sidebarOpen)} menuItems={menuItems} role={role} />
      
      <div className={`main-content ${sidebarOpen ? 'sidebar-open' : 'sidebar-closed'}`}>
        <header className="top-header">
          <button onClick={() => setSidebarOpen(!sidebarOpen)} className="menu-toggle">☰</button>
          <div className="user-info">
            <span className="user-name">{user?.full_name}</span>
            <span className="user-role">{user?.role}</span>
          </div>
        </header>
        
        <main className="page-content">{children}</main>
      </div>
    </div>
  );
};

// ADMIN PAGES (DETAILED)
const AdminDashboard = () => {
  const [stats, setStats] = useState(null);
  const [enrollments, setEnrollments] = useState([]);
  const [courses, setCourses] = useState([]);
  const { user } = useAuth();

  useEffect(() => {
    const loadData = async () => {
      const dashboardStats = await mockService.getDashboardStats('admin', user?.id);
      setStats(dashboardStats);
      
      const allEnrollments = await mockService.getEnrollments({});
      setEnrollments(allEnrollments.slice(0, 5));
      
      const pendingCourses = await mockService.getCourses({ status: 'pending_approval' });
      setCourses(pendingCourses);
    };
    loadData();
  }, [user]);

  if (!stats) return <div className="loading-screen">Loading...</div>;

  return (
    <div className="page-wrapper">
      <div className="page-header">
        <h1 className="page-title">Admin Dashboard</h1>
        <p className="page-subtitle">Overview of system metrics and activities</p>
      </div>

      <div className="stats-grid">
        <StatCard icon="👥" label="Total Students" value={stats.total_students} trend="Active learners" color="blue" />
        <StatCard icon="👨‍🏫" label="Active Mentors" value={stats.total_mentors} trend="Teaching now" color="purple" />
        <StatCard icon="📚" label="Total Courses" value={stats.total_courses} trend={`${stats.active_courses} active`} color="green" />
        <StatCard icon="⏳" label="Pending Approvals" value={stats.pending_approvals} trend="Needs review" color="orange" />
      </div>

      <div className="dashboard-grid">
        <div className="dashboard-card">
          <div className="card-header">
            <h3>Recent Enrollments</h3>
            <button className="btn-text">View All</button>
          </div>
          <div className="activity-list">
            {enrollments.length === 0 ? (
              <div className="empty-state">
                <p>📚 No recent enrollments</p>
              </div>
            ) : (
              enrollments.map(enroll => (
                <div key={enroll.id} className="activity-item">
                  <div className="activity-avatar">👤</div>
                  <div className="activity-content">
                    <p className="activity-title">{enroll.student_name} enrolled in {enroll.course_name}</p>
                    <p className="activity-time">{new Date(enroll.enrolled_at).toLocaleDateString()}</p>
                  </div>
                </div>
              ))
            )}
          </div>
        </div>

        <div className="dashboard-card">
          <div className="card-header">
            <h3>Course Performance</h3>
            <select className="filter-select-sm">
              <option>Last 7 days</option>
              <option>Last 30 days</option>
              <option>Last 3 months</option>
            </select>
          </div>
          <div className="chart-placeholder">
            <div className="chart-bars">
              {[40, 65, 45, 80, 55, 70, 85].map((height, i) => (
                <div key={i} className="chart-bar" style={{ height: `${height}%` }}>
                  <span className="chart-label">Day {i+1}</span>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>

      <div className="dashboard-card">
        <div className="card-header">
          <h3>Pending Course Approvals</h3>
          <span className="badge badge-warning">{courses.length} Items</span>
        </div>
        {courses.length === 0 ? (
          <div className="empty-state">
            <p>✅ No pending approvals</p>
          </div>
        ) : (
          <DataTable 
            columns={['Course Name', 'Mentor', 'Category', 'Level', 'Status']}
            data={courses.map(course => [
              course.title,
              course.instructor_name,
              course.category,
              course.level,
              <span className="badge badge-warning">Pending Approval</span>
            ])}
            actions={[
              { icon: '✓', label: 'Approve', variant: 'success' },
              { icon: '✕', label: 'Reject', variant: 'danger' }
            ]}
          />
        )}
      </div>
    </div>
  );
};

const CoursesManagement = () => {
  const [showModal, setShowModal] = useState(false);
  const [showDeleteModal, setShowDeleteModal] = useState(false);
  const [courses, setCourses] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [editingCourse, setEditingCourse] = useState(null);
  const [courseToDelete, setCourseToDelete] = useState(null);
  const [filters, setFilters] = useState({ category: 'All', status: 'All', level: 'All', search: '' });
  const [formData, setFormData] = useState({
    title: '', description: '', category: 'Programming', level: 'Beginner', 
    duration: '', instructor_id: '', instructor_name: '', price: '', status: 'draft',
    total_lessons: '', image: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)'
  });
  const { user } = useAuth();
  const toast = useToast();

  useEffect(() => {
    loadCourses();
  }, [filters]);

  const loadCourses = async () => {
    setIsLoading(true);
    const data = await mockService.getCourses(filters);
    setCourses(data);
    setIsLoading(false);
  };

  const isFormValid = formData.title.trim().length > 0 && formData.description.trim().length > 0;

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!isFormValid) return;

    try {
      if (editingCourse) {
        await mockService.updateCourse(editingCourse.id, formData);
        toast.success('Course updated successfully!');
      } else {
        await mockService.createCourse({...formData, instructor_id: user.id, instructor_name: user.full_name});
        toast.success('Course created successfully!');
      }
      setShowModal(false);
      resetForm();
      loadCourses();
    } catch (error) {
      toast.error('Error: ' + error.message);
    }
  };

  const handleEdit = (course) => {
    setEditingCourse(course);
    setFormData(course);
    setShowModal(true);
  };

  const handleDelete = async () => {
    if (courseToDelete) {
      try {
        await mockService.deleteCourse(courseToDelete.id);
        toast.success('Course deleted successfully!');
        setShowDeleteModal(false);
        setCourseToDelete(null);
        loadCourses();
      } catch (error) {
        toast.error('Error deleting course: ' + error.message);
      }
    }
  };

  const resetForm = () => {
    setEditingCourse(null);
    setFormData({
      title: '', description: '', category: 'Programming', level: 'Beginner',
      duration: '', instructor_id: '', instructor_name: '', price: '', status: 'draft',
      total_lessons: '', image: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)'
    });
  };
  
  return (
    <div className="page-wrapper">
      <div className="page-header">
        <div>
          <h1 className="page-title">Courses Management</h1>
          <p className="page-subtitle">Create and manage all courses</p>
        </div>
        <button className="btn-primary" onClick={() => { resetForm(); setShowModal(true); }}>
          + Create New Course
        </button>
      </div>

      <div className="search-filter-bar">
        <div className="search-box">
          <span className="search-icon">🔍</span>
          <input type="text" placeholder="Search courses..." 
            onChange={(e) => setFilters({...filters, search: e.target.value})} />
        </div>
        <div className="filter-group">
          <select className="filter-select" onChange={(e) => setFilters({...filters, category: e.target.value})}>
            <option value="All">All Categories</option>
            <option value="Programming">Programming</option>
            <option value="Design">Design</option>
            <option value="Business">Business</option>
            <option value="Data Science">Data Science</option>
          </select>
          <select className="filter-select" onChange={(e) => setFilters({...filters, status: e.target.value})}>
            <option value="All">All Status</option>
            <option value="active">Active</option>
            <option value="draft">Draft</option>
            <option value="pending_approval">Pending Approval</option>
          </select>
          <select className="filter-select" onChange={(e) => setFilters({...filters, level: e.target.value})}>
            <option value="All">All Levels</option>
            <option value="Beginner">Beginner</option>
            <option value="Intermediate">Intermediate</option>
            <option value="Advanced">Advanced</option>
          </select>
        </div>
      </div>

      {isLoading ? (
        <div className="courses-grid">
          {Array.from({ length: 6 }).map((_, i) => (
            <SkeletonCard key={i} />
          ))}
        </div>
      ) : courses.length === 0 ? (
        <motion.div 
          className="empty-state-large"
          initial={{ opacity: 0, scale: 0.9 }}
          animate={{ opacity: 1, scale: 1 }}
        >
          <div className="empty-icon">📚</div>
          <h3>No Courses Found</h3>
          <p>Create your first course to get started</p>
          <motion.button 
            className="btn-primary" 
            onClick={() => setShowModal(true)}
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
          >
            + Create Course
          </motion.button>
        </motion.div>
      ) : (
        <motion.div 
          className="courses-grid"
          initial="hidden"
          animate="visible"
          variants={{
            visible: { transition: { staggerChildren: 0.1 } }
          }}
        >
          {courses.map(course => (
            <div key={course.id} className="course-card">
              <div className="course-image" style={{ background: course.image }}>
                <span className="course-badge">{course.category}</span>
                <div className="course-actions-overlay">
                  <button className="btn-icon-white" onClick={() => handleEdit(course)} title="Edit">✏️</button>
                  <button className="btn-icon-white" onClick={() => { setCourseToDelete(course); setShowDeleteModal(true); }} title="Delete">🗑️</button>
                </div>
              </div>
              <div className="course-body">
                <h3 className="course-title">{course.title}</h3>
                <p className="course-instructor">👨‍🏫 {course.instructor_name}</p>
                <div className="course-meta">
                  <span className="meta-item">⏱️ {course.duration}</span>
                  <span className="meta-item">📊 {course.level}</span>
                  <span className="meta-item">👥 {course.total_students} students</span>
                </div>
                <div className="course-footer">
                  <span className={`badge badge-${course.status === 'active' ? 'success' : course.status === 'draft' ? 'secondary' : 'warning'}`}>
                    {course.status.replace('_', ' ')}
                  </span>
                  <span className="course-price">${course.price}</span>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}

      <Modal isOpen={showModal} onClose={() => { setShowModal(false); resetForm(); }} 
        title={editingCourse ? 'Edit Course' : 'Create New Course'}>
        <form className="modal-form" onSubmit={handleSubmit}>
          <div className="form-group">
            <label>Course Title *</label>
            <input type="text" placeholder="Enter course title" required
              value={formData.title} onChange={(e) => setFormData({...formData, title: e.target.value})} />
          </div>
          <div className="form-row">
            <div className="form-group">
              <label>Category *</label>
              <select required value={formData.category} onChange={(e) => setFormData({...formData, category: e.target.value})}>
                <option value="Programming">Programming</option>
                <option value="Design">Design</option>
                <option value="Business">Business</option>
                <option value="Data Science">Data Science</option>
              </select>
            </div>
            <div className="form-group">
              <label>Level *</label>
              <select required value={formData.level} onChange={(e) => setFormData({...formData, level: e.target.value})}>
                <option value="Beginner">Beginner</option>
                <option value="Intermediate">Intermediate</option>
                <option value="Advanced">Advanced</option>
              </select>
            </div>
          </div>
          <div className="form-row">
            <div className="form-group">
              <label>Duration</label>
              <input type="text" placeholder="e.g. 8 weeks" 
                value={formData.duration} onChange={(e) => setFormData({...formData, duration: e.target.value})} />
            </div>
            <div className="form-group">
              <label>Price ($)</label>
              <input type="number" placeholder="299" 
                value={formData.price} onChange={(e) => setFormData({...formData, price: e.target.value})} />
            </div>
          </div>
          <div className="form-group">
            <label>Total Lessons</label>
            <input type="number" placeholder="45" 
              value={formData.total_lessons} onChange={(e) => setFormData({...formData, total_lessons: e.target.value})} />
          </div>
          <div className="form-group">
            <label>Description *</label>
            <textarea rows="4" placeholder="Course description..." required
              value={formData.description} onChange={(e) => setFormData({...formData, description: e.target.value})}></textarea>
          </div>
          <div className="form-group">
            <label>Status</label>
            <select value={formData.status} onChange={(e) => setFormData({...formData, status: e.target.value})}>
              <option value="draft">Draft</option>
              <option value="active">Active</option>
              <option value="pending_approval">Pending Approval</option>
            </select>
          </div>
          <div className="modal-actions">
            <button type="button" className="btn-secondary" onClick={() => { setShowModal(false); resetForm(); }}>Cancel</button>
            <button type="submit" className="btn-primary">{editingCourse ? 'Update' : 'Create'} Course</button>
          </div>
        </form>
      </Modal>

      <Modal isOpen={showDeleteModal} onClose={() => setShowDeleteModal(false)} title="Delete Course">
        <div className="modal-form">
          <p>Are you sure you want to delete "<strong>{courseToDelete?.title}</strong>"?</p>
          <p className="text-muted">This action cannot be undone. All related batches and enrollments will be affected.</p>
          <div className="modal-actions">
            <button type="button" className="btn-secondary" onClick={() => setShowDeleteModal(false)}>Cancel</button>
            <button type="button" className="btn-danger" onClick={handleDelete}>Delete Course</button>
          </div>
        </div>
      </Modal>
    </div>
  );
};

const MentorManagement = () => {
  const [showModal, setShowModal] = useState(false);
  const [mentors, setMentors] = useState([]);
  const [editingMentor, setEditingMentor] = useState(null);
  const [filter, setFilter] = useState('All');

  useEffect(() => {
    loadMentors();
  }, [filter]);

  const loadMentors = async () => {
    const allMentors = await mockService.getUsers('mentor');
    if (filter === 'All') {
      setMentors(allMentors);
    } else {
      setMentors(allMentors.filter(m => m.department === filter));
    }
  };

  const handleEdit = (mentor) => {
    setEditingMentor(mentor);
    setShowModal(true);
  };

  const handleUpdate = async (e) => {
    e.preventDefault();
    if (editingMentor) {
      await mockService.updateUser(editingMentor.id, editingMentor);
      alert('Mentor updated successfully!');
      setShowModal(false);
      setEditingMentor(null);
      loadMentors();
    }
  };
  
  return (
    <div className="page-wrapper">
      <div className="page-header">
        <div>
          <h1 className="page-title">Mentor Management</h1>
          <p className="page-subtitle">Manage mentor accounts and assignments</p>
        </div>
      </div>

      <div className="search-filter-bar">
        <div className="search-box">
          <span className="search-icon">🔍</span>
          <input type="text" placeholder="Search mentors..." />
        </div>
        <div className="filter-group">
          <select className="filter-select" onChange={(e) => setFilter(e.target.value)}>
            <option value="All">All Departments</option>
            <option value="Programming">Programming</option>
            <option value="Design">Design</option>
            <option value="Business">Business</option>
            <option value="Data Science">Data Science</option>
          </select>
        </div>
      </div>

      <div className="dashboard-card">
        {mentors.length === 0 ? (
          <div className="empty-state">
            <p>👨‍🏫 No mentors found</p>
          </div>
        ) : (
          <DataTable 
            columns={['Name', 'Email', 'Department', 'Courses', 'Students', 'Rating', 'Status']}
            data={mentors.map((mentor, idx) => [
              mentor.full_name,
              mentor.email,
              mentor.department || 'N/A',
              mentor.total_courses || 0,
              mentor.total_students || 0,
              mentor.rating ? `⭐ ${mentor.rating}` : 'N/A',
              <span className={`badge badge-${mentor.status === 'active' ? 'success' : 'warning'}`}>
                {mentor.status ? mentor.status.replace('_', ' ') : 'Active'}
              </span>
            ])}
            actions={[
              { icon: '✏️', label: 'Edit' }
            ]}
          />
        )}
      </div>

      <Modal isOpen={showModal} onClose={() => { setShowModal(false); setEditingMentor(null); }} title="Edit Mentor">
        <form className="modal-form" onSubmit={handleUpdate}>
          <div className="form-group">
            <label>Full Name</label>
            <input type="text" placeholder="Enter full name" required
              value={editingMentor?.full_name || ''} 
              onChange={(e) => setEditingMentor({...editingMentor, full_name: e.target.value})} />
          </div>
          <div className="form-group">
            <label>Email</label>
            <input type="email" placeholder="Enter email address" required
              value={editingMentor?.email || ''} 
              onChange={(e) => setEditingMentor({...editingMentor, email: e.target.value})} />
          </div>
          <div className="form-group">
            <label>Department</label>
            <select value={editingMentor?.department || 'Programming'} 
              onChange={(e) => setEditingMentor({...editingMentor, department: e.target.value})}>
              <option value="Programming">Programming</option>
              <option value="Design">Design</option>
              <option value="Business">Business</option>
              <option value="Data Science">Data Science</option>
            </select>
          </div>
          <div className="form-group">
            <label>Specialization</label>
            <input type="text" placeholder="e.g. React, Node.js" 
              value={editingMentor?.specialization || ''} 
              onChange={(e) => setEditingMentor({...editingMentor, specialization: e.target.value})} />
          </div>
          <div className="form-group">
            <label>Status</label>
            <select value={editingMentor?.status || 'active'} 
              onChange={(e) => setEditingMentor({...editingMentor, status: e.target.value})}>
              <option value="active">Active</option>
              <option value="on_leave">On Leave</option>
              <option value="inactive">Inactive</option>
            </select>
          </div>
          <div className="modal-actions">
            <button type="button" className="btn-secondary" onClick={() => { setShowModal(false); setEditingMentor(null); }}>Cancel</button>
            <button type="submit" className="btn-primary">Update Mentor</button>
          </div>
        </form>
      </Modal>
    </div>
  );
};

const StudentManagement = () => {
  const [students, setStudents] = useState([]);
  const [showModal, setShowModal] = useState(false);
  const [selectedStudent, setSelectedStudent] = useState(null);

  useEffect(() => {
    loadStudents();
  }, []);

  const loadStudents = async () => {
    const allStudents = await mockService.getUsers('student');
    setStudents(allStudents);
  };

  const handleViewProfile = (student) => {
    setSelectedStudent(student);
    setShowModal(true);
  };

  return (
    <div className="page-wrapper">
      <div className="page-header">
        <div>
          <h1 className="page-title">Student Management</h1>
          <p className="page-subtitle">Manage student accounts and enrollments</p>
        </div>
      </div>

      <div className="search-filter-bar">
        <div className="search-box">
          <span className="search-icon">🔍</span>
          <input type="text" placeholder="Search students..." />
        </div>
      </div>

      <div className="dashboard-card">
        {students.length === 0 ? (
          <div className="empty-state">
            <p>👥 No students found</p>
          </div>
        ) : (
          <DataTable 
            columns={['Name', 'Email', 'Username', 'Enrolled Courses', 'Attendance %', 'Join Date']}
            data={students.map(student => [
              student.full_name,
              student.email,
              student.username,
              student.enrolled_courses || 0,
              student.attendance_percentage ? `${student.attendance_percentage}%` : 'N/A',
              new Date(student.created_at).toLocaleDateString()
            ])}
            actions={[
              { icon: '👁️', label: 'View Profile' }
            ]}
          />
        )}
      </div>

      <Modal isOpen={showModal} onClose={() => { setShowModal(false); setSelectedStudent(null); }} title="Student Profile">
        {selectedStudent && (
          <div className="profile-view">
            <div className="profile-header">
              <div className="profile-avatar">👤</div>
              <div>
                <h3>{selectedStudent.full_name}</h3>
                <p className="text-muted">{selectedStudent.email}</p>
              </div>
            </div>
            <div className="profile-stats">
              <div className="stat-item">
                <span className="stat-label">Enrolled Courses</span>
                <span className="stat-value">{selectedStudent.enrolled_courses || 0}</span>
              </div>
              <div className="stat-item">
                <span className="stat-label">Completed Courses</span>
                <span className="stat-value">{selectedStudent.completed_courses || 0}</span>
              </div>
              <div className="stat-item">
                <span className="stat-label">Attendance</span>
                <span className="stat-value">{selectedStudent.attendance_percentage || 0}%</span>
              </div>
              <div className="stat-item">
                <span className="stat-label">Tasks Completed</span>
                <span className="stat-value">{selectedStudent.completed_tasks || 0}/{selectedStudent.total_tasks || 0}</span>
              </div>
            </div>
            <div className="modal-actions">
              <button type="button" className="btn-secondary" onClick={() => setShowModal(false)}>Close</button>
            </div>
          </div>
        )}
      </Modal>
    </div>
  );
};

const ReportsOverview = () => {
  const [activeTab, setActiveTab] = useState('overview');
  const [attendance, setAttendance] = useState([]);
  const [grades, setGrades] = useState([]);
  const [courses, setCourses] = useState([]);

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    const attendanceData = await mockService.getAttendance({});
    setAttendance(attendanceData);
    
    const gradesData = await mockService.getGrades({});
    setGrades(gradesData);
    
    const coursesData = await mockService.getCourses({});
    setCourses(coursesData.sort((a, b) => b.total_students - a.total_students).slice(0, 5));
  };

  return (
    <div className="page-wrapper">
      <div className="page-header">
        <div>
          <h1 className="page-title">Reports & Analytics</h1>
          <p className="page-subtitle">View attendance, grades and system analytics</p>
        </div>
        <button className="btn-primary">📥 Export Report</button>
      </div>

      <div className="tabs-container">
        <div className="tabs">
          <button className={`tab ${activeTab === 'overview' ? 'active' : ''}`} 
            onClick={() => setActiveTab('overview')}>Overview</button>
          <button className={`tab ${activeTab === 'attendance' ? 'active' : ''}`} 
            onClick={() => setActiveTab('attendance')}>Attendance</button>
          <button className={`tab ${activeTab === 'grades' ? 'active' : ''}`} 
            onClick={() => setActiveTab('grades')}>Grades</button>
        </div>
      </div>

      {activeTab === 'overview' && (
        <>
          <div className="stats-grid">
            <StatCard icon="📚" label="Total Courses" value={courses.length} trend="Active" color="blue" />
            <StatCard icon="📝" label="Attendance Records" value={attendance.length} trend="Total marked" color="green" />
            <StatCard icon="🎯" label="Grades Recorded" value={grades.length} trend="Assessments" color="purple" />
            <StatCard icon="⭐" label="Avg Grade" value="B+" trend="Overall performance" color="orange" />
          </div>

          <div className="dashboard-card">
            <div className="card-header">
              <h3>Top Performing Courses</h3>
            </div>
            {courses.length === 0 ? (
              <div className="empty-state">
                <p>📊 No course data available</p>
              </div>
            ) : (
              <div className="ranking-list">
                {courses.map((course, i) => (
                  <div key={course.id} className="ranking-item">
                    <span className="rank-number">#{i+1}</span>
                    <div className="rank-content">
                      <p className="rank-title">{course.title}</p>
                      <p className="text-muted">{course.instructor_name}</p>
                    </div>
                    <span className="rank-value">{course.total_students} students</span>
                  </div>
                ))}
              </div>
            )}
          </div>
        </>
      )}

      {activeTab === 'attendance' && (
        <div className="dashboard-card">
          <div className="card-header">
            <h3>Attendance Records</h3>
            <p className="text-muted">All attendance entries</p>
          </div>
          {attendance.length === 0 ? (
            <div className="empty-state">
              <p>📅 No attendance records found</p>
            </div>
          ) : (
            <DataTable 
              columns={['Date', 'Batch', 'Student', 'Status', 'Marked By']}
              data={attendance.map(record => [
                new Date(record.date).toLocaleDateString(),
                record.batch_name,
                record.student_name,
                <span className={`badge badge-${record.status === 'present' ? 'success' : 'danger'}`}>
                  {record.status}
                </span>,
                'Mentor'
              ])}
            />
          )}
        </div>
      )}

      {activeTab === 'grades' && (
        <div className="dashboard-card">
          <div className="card-header">
            <h3>Grade Records</h3>
            <p className="text-muted">All assessment grades</p>
          </div>
          {grades.length === 0 ? (
            <div className="empty-state">
              <p>🎯 No grade records found</p>
            </div>
          ) : (
            <DataTable 
              columns={['Student', 'Course', 'Assessment', 'Score', 'Grade', 'Date']}
              data={grades.map(grade => [
                grade.student_name,
                grade.course_name,
                `${grade.assessment_type}: ${grade.assessment_name}`,
                `${grade.score}/${grade.max_score}`,
                <span className={`badge badge-${grade.grade.includes('A') ? 'success' : grade.grade.includes('B') ? 'primary' : 'warning'}`}>
                  {grade.grade}
                </span>,
                new Date(grade.graded_at).toLocaleDateString()
              ])}
            />
          )}
        </div>
      )}
    </div>
  );
};

const CourseApproval = () => {
  return (
    <div className="page-wrapper">
      <div className="page-header">
        <h1 className="page-title">Course Approval</h1>
        <p className="page-subtitle">Review and approve course submissions</p>
      </div>

      <div className="tabs-container">
        <div className="tabs">
          <button className="tab active">Pending <span className="tab-count">12</span></button>
          <button className="tab">Approved <span className="tab-count">87</span></button>
          <button className="tab">Rejected <span className="tab-count">5</span></button>
        </div>
      </div>

      <div className="approval-list">
        {[1,2,3].map(i => (
          <div key={i} className="approval-card">
            <div className="approval-header">
              <div>
                <h3>Course Title {i}</h3>
                <p className="text-muted">Submitted by Mentor Name • 2 days ago</p>
              </div>
              <span className="badge badge-warning">Pending Review</span>
            </div>
            <div className="approval-body">
              <div className="approval-details">
                <div className="detail-item">
                  <span className="detail-label">Category:</span>
                  <span>Programming</span>
                </div>
                <div className="detail-item">
                  <span className="detail-label">Duration:</span>
                  <span>8 weeks</span>
                </div>
                <div className="detail-item">
                  <span className="detail-label">Level:</span>
                  <span>Intermediate</span>
                </div>
                <div className="detail-item">
                  <span className="detail-label">Modules:</span>
                  <span>12</span>
                </div>
              </div>
              <p className="approval-description">
                This course covers advanced concepts in modern web development...
              </p>
            </div>
            <div className="approval-actions">
              <button className="btn-secondary">📄 View Details</button>
              <button className="btn-danger">✕ Reject</button>
              <button className="btn-success">✓ Approve</button>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

const BatchDownloads = () => {
  const [selected, setSelected] = useState([]);
  
  return (
    <div className="page-wrapper">
      <div className="page-header">
        <div>
          <h1 className="page-title">Batch Video Downloads</h1>
          <p className="page-subtitle">Download course videos in batches</p>
        </div>
        <button className="btn-primary" disabled={selected.length === 0}>
          📥 Download Selected ({selected.length})
        </button>
      </div>

      <SearchFilter filters={[{ label: 'Course', options: ['All Courses', 'React', 'Python'] }]} />

      <div className="dashboard-card">
        <div className="file-list">
          {[1,2,3,4,5,6].map(i => (
            <div key={i} className="file-item">
              <input type="checkbox" onChange={(e) => {
                if (e.target.checked) setSelected([...selected, i]);
                else setSelected(selected.filter(x => x !== i));
              }} />
              <div className="file-icon">🎥</div>
              <div className="file-info">
                <p className="file-name">Module {i} - Introduction to React Hooks.mp4</p>
                <p className="file-meta">Course: React Masterclass • 245 MB • Uploaded 2 days ago</p>
              </div>
              <button className="btn-icon">⬇️</button>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};

const MockInterviews = () => {
  const [showModal, setShowModal] = useState(false);
  
  return (
    <div className="page-wrapper">
      <div className="page-header">
        <div>
          <h1 className="page-title">Mock Interview Appointments</h1>
          <p className="page-subtitle">Schedule and manage mock interviews</p>
        </div>
        <button className="btn-primary" onClick={() => setShowModal(true)}>+ Schedule Interview</button>
      </div>

      <div className="calendar-view">
        <div className="calendar-header">
          <button className="btn-icon">←</button>
          <h3>January 2024</h3>
          <button className="btn-icon">→</button>
        </div>
        <div className="calendar-grid">
          <div className="calendar-day-header">Sun</div>
          <div className="calendar-day-header">Mon</div>
          <div className="calendar-day-header">Tue</div>
          <div className="calendar-day-header">Wed</div>
          <div className="calendar-day-header">Thu</div>
          <div className="calendar-day-header">Fri</div>
          <div className="calendar-day-header">Sat</div>
          
          {[...Array(35)].map((_, i) => (
            <div key={i} className={`calendar-day ${i % 7 === 0 || i % 7 === 6 ? 'weekend' : ''}`}>
              <span className="day-number">{i < 31 ? i+1 : ''}</span>
              {[10, 15, 20, 22].includes(i) && (
                <div className="interview-dot" title="2 interviews scheduled"></div>
              )}
            </div>
          ))}
        </div>
      </div>

      <div className="dashboard-card">
        <h3>Upcoming Interviews</h3>
        <DataTable 
          columns={['Student', 'Interviewer', 'Date & Time', 'Type', 'Status']}
          data={[
            ['John Doe', 'Sarah Wilson', 'Jan 15, 2024 - 10:00 AM', 'Technical', <span className="badge badge-success">Confirmed</span>],
            ['Jane Smith', 'Mike Johnson', 'Jan 16, 2024 - 2:00 PM', 'HR Round', <span className="badge badge-warning">Pending</span>],
            ['Bob Brown', 'Sarah Wilson', 'Jan 18, 2024 - 11:00 AM', 'Technical', <span className="badge badge-success">Confirmed</span>]
          ]}
          actions={[
            { icon: '✏️', label: 'Reschedule' },
            { icon: '✕', label: 'Cancel', variant: 'danger' }
          ]}
        />
      </div>

      <Modal isOpen={showModal} onClose={() => setShowModal(false)} title="Schedule Mock Interview">
        <form className="modal-form">
          <div className="form-group">
            <label>Student</label>
            <select><option>Select student</option></select>
          </div>
          <div className="form-group">
            <label>Interviewer</label>
            <select><option>Select interviewer</option></select>
          </div>
          <div className="form-row">
            <div className="form-group">
              <label>Date</label>
              <input type="date" />
            </div>
            <div className="form-group">
              <label>Time</label>
              <input type="time" />
            </div>
          </div>
          <div className="form-group">
            <label>Interview Type</label>
            <select>
              <option>Technical</option>
              <option>HR Round</option>
              <option>Behavioral</option>
            </select>
          </div>
          <div className="modal-actions">
            <button type="button" className="btn-secondary" onClick={() => setShowModal(false)}>Cancel</button>
            <button type="submit" className="btn-primary">Schedule</button>
          </div>
        </form>
      </Modal>
    </div>
  );
};

const AssignmentsGrading = () => {
  const [activeTab, setActiveTab] = useState('pending');
  const [submissions, setSubmissions] = useState([]);
  const [showGradeModal, setShowGradeModal] = useState(false);
  const [selectedSubmission, setSelectedSubmission] = useState(null);
  const [gradeData, setGradeData] = useState({ score: '', feedback: '' });
  const { user } = useAuth();

  useEffect(() => {
    loadSubmissions();
  }, [activeTab]);

  const loadSubmissions = async () => {
    const allSubmissions = await mockService.getSubmissions({});
    if (activeTab === 'pending') {
      setSubmissions(allSubmissions.filter(s => s.status === 'pending'));
    } else {
      setSubmissions(allSubmissions.filter(s => s.status === 'graded'));
    }
  };

  const handleGrade = (submission) => {
    setSelectedSubmission(submission);
    setGradeData({ score: '', feedback: '' });
    setShowGradeModal(true);
  };

  const submitGrade = async (e) => {
    e.preventDefault();
    try {
      await mockService.gradeSubmission(selectedSubmission.id, {
        score: parseInt(gradeData.score),
        feedback: gradeData.feedback,
        graded_by: user.id
      });
      alert('Submission graded successfully!');
      setShowGradeModal(false);
      setSelectedSubmission(null);
      loadSubmissions();
    } catch (error) {
      alert('Error: ' + error.message);
    }
  };

  const pendingCount = submissions.filter(s => s.status === 'pending').length;
  const gradedCount = submissions.filter(s => s.status === 'graded').length;

  return (
    <div className="page-wrapper">
      <div className="page-header">
        <h1 className="page-title">Assignments & Submissions</h1>
        <p className="page-subtitle">Review and grade student assignments</p>
      </div>

      <div className="tabs-container">
        <div className="tabs">
          <button className={`tab ${activeTab === 'pending' ? 'active' : ''}`} 
            onClick={() => setActiveTab('pending')}>
            Pending <span className="tab-count">{pendingCount}</span>
          </button>
          <button className={`tab ${activeTab === 'graded' ? 'active' : ''}`} 
            onClick={() => setActiveTab('graded')}>
            Graded <span className="tab-count">{gradedCount}</span>
          </button>
        </div>
      </div>

      {submissions.length === 0 ? (
        <div className="empty-state-large">
          <div className="empty-icon">📝</div>
          <h3>No {activeTab} submissions</h3>
          <p>All submissions have been processed</p>
        </div>
      ) : (
        <div className="assignment-list">
          {submissions.map(submission => (
            <div key={submission.id} className="assignment-card">
              <div className="assignment-header">
                <div>
                  <h3>{submission.task_title}</h3>
                  <p className="text-muted">Submitted by: {submission.student_name}</p>
                </div>
                <span className={`badge badge-${submission.status === 'pending' ? 'warning' : 'success'}`}>
                  {submission.status}
                </span>
              </div>
              <div className="assignment-body">
                <div className="assignment-meta">
                  <span>📅 Submitted: {new Date(submission.submitted_at).toLocaleDateString()}</span>
                  {submission.submission_url && <span>🔗 URL provided</span>}
                </div>
                {submission.submission_text && (
                  <p className="assignment-description">{submission.submission_text}</p>
                )}
                {submission.score !== null && (
                  <div className="grade-display">
                    <strong>Score: {submission.score}/100</strong>
                    {submission.feedback && <p>Feedback: {submission.feedback}</p>}
                  </div>
                )}
              </div>
              <div className="assignment-actions">
                {submission.submission_url && (
                  <a href={submission.submission_url} target="_blank" rel="noopener noreferrer" className="btn-secondary">
                    👁️ View Submission
                  </a>
                )}
                {submission.status === 'pending' && (
                  <button className="btn-primary" onClick={() => handleGrade(submission)}>📝 Grade</button>
                )}
              </div>
            </div>
          ))}
        </div>
      )}

      <Modal isOpen={showGradeModal} onClose={() => setShowGradeModal(false)} title="Grade Submission">
        <form className="modal-form" onSubmit={submitGrade}>
          {selectedSubmission && (
            <>
              <div className="form-group">
                <label>Student: <strong>{selectedSubmission.student_name}</strong></label>
                <label>Task: <strong>{selectedSubmission.task_title}</strong></label>
              </div>
              <div className="form-group">
                <label>Score (out of 100) *</label>
                <input type="number" min="0" max="100" required
                  value={gradeData.score} 
                  onChange={(e) => setGradeData({...gradeData, score: e.target.value})} 
                  placeholder="Enter score" />
              </div>
              <div className="form-group">
                <label>Feedback *</label>
                <textarea rows="4" required
                  value={gradeData.feedback} 
                  onChange={(e) => setGradeData({...gradeData, feedback: e.target.value})} 
                  placeholder="Provide feedback to the student..."></textarea>
              </div>
            </>
          )}
          <div className="modal-actions">
            <button type="button" className="btn-secondary" onClick={() => setShowGradeModal(false)}>Cancel</button>
            <button type="submit" className="btn-primary">Submit Grade</button>
          </div>
        </form>
      </Modal>
    </div>
  );
};

const FeeAlerts = () => {
  return (
    <div className="page-wrapper">
      <div className="page-header">
        <div>
          <h1 className="page-title">Fee Reminder Alerts</h1>
          <p className="page-subtitle">Manage fee payment reminders</p>
        </div>
        <button className="btn-primary">📧 Send Bulk Reminder</button>
      </div>

      <div className="stats-grid">
        <StatCard icon="💵" label="Total Pending" value="$12,450" trend="15 students" color="orange" />
        <StatCard icon="✅" label="Paid This Month" value="$38,900" trend="102 students" color="green" />
        <StatCard icon="⚠️" label="Overdue" value="$3,200" trend="5 students" color="red" />
        <StatCard icon="📊" label="Collection Rate" value="94%" trend="↑ 3%" color="blue" />
      </div>

      <div className="dashboard-card">
        <div className="card-header">
          <h3>Payment Status</h3>
          <div className="tabs-inline">
            <button className="tab-inline active">All</button>
            <button className="tab-inline">Pending</button>
            <button className="tab-inline">Overdue</button>
            <button className="tab-inline">Paid</button>
          </div>
        </div>
        <DataTable 
          columns={['Student', 'Course', 'Amount', 'Due Date', 'Status', 'Last Reminder']}
          data={[
            ['Alice Johnson', 'React Masterclass', '$499', 'Jan 20, 2024', <span className="badge badge-warning">Pending</span>, 'Jan 10'],
            ['Bob Smith', 'Python Course', '$399', 'Jan 18, 2024', <span className="badge badge-danger">Overdue</span>, 'Jan 15'],
            ['Carol White', 'UI/UX Design', '$599', 'Jan 25, 2024', <span className="badge badge-success">Paid</span>, '-'],
            ['David Brown', 'Data Science', '$799', 'Jan 22, 2024', <span className="badge badge-warning">Pending</span>, 'Jan 12']
          ]}
          actions={[
            { icon: '📧', label: 'Send Reminder' },
            { icon: '💳', label: 'Payment Details' },
            { icon: '👁️', label: 'View' }
          ]}
        />
      </div>
    </div>
  );
};

const SecurityProctoring = () => {
  return (
    <div className="page-wrapper">
      <div className="page-header">
        <h1 className="page-title">Security & Proctoring Setup</h1>
        <p className="page-subtitle">Configure security and proctoring settings</p>
      </div>

      <div className="settings-grid">
        <div className="dashboard-card">
          <h3>Exam Proctoring Settings</h3>
          <div className="settings-list">
            <div className="setting-item">
              <div>
                <p className="setting-title">Enable Camera Monitoring</p>
                <p className="setting-desc">Require students to enable camera during exams</p>
              </div>
              <label className="toggle">
                <input type="checkbox" defaultChecked />
                <span className="toggle-slider"></span>
              </label>
            </div>
            <div className="setting-item">
              <div>
                <p className="setting-title">Screen Recording</p>
                <p className="setting-desc">Record student screens during assessments</p>
              </div>
              <label className="toggle">
                <input type="checkbox" defaultChecked />
                <span className="toggle-slider"></span>
              </label>
            </div>
            <div className="setting-item">
              <div>
                <p className="setting-title">Browser Lockdown</p>
                <p className="setting-desc">Prevent tab switching during exams</p>
              </div>
              <label className="toggle">
                <input type="checkbox" />
                <span className="toggle-slider"></span>
              </label>
            </div>
            <div className="setting-item">
              <div>
                <p className="setting-title">AI Behavior Analysis</p>
                <p className="setting-desc">Detect suspicious behavior patterns</p>
              </div>
              <label className="toggle">
                <input type="checkbox" defaultChecked />
                <span className="toggle-slider"></span>
              </label>
            </div>
          </div>
        </div>

        <div className="dashboard-card">
          <h3>Access Control</h3>
          <div className="settings-list">
            <div className="setting-item">
              <div>
                <p className="setting-title">Two-Factor Authentication</p>
                <p className="setting-desc">Require 2FA for all admin accounts</p>
              </div>
              <label className="toggle">
                <input type="checkbox" defaultChecked />
                <span className="toggle-slider"></span>
              </label>
            </div>
            <div className="setting-item">
              <div>
                <p className="setting-title">IP Whitelisting</p>
                <p className="setting-desc">Restrict access to specific IP ranges</p>
              </div>
              <label className="toggle">
                <input type="checkbox" />
                <span className="toggle-slider"></span>
              </label>
            </div>
            <div className="setting-item">
              <div>
                <p className="setting-title">Session Timeout</p>
                <p className="setting-desc">Auto-logout after inactivity</p>
              </div>
              <select className="setting-select">
                <option>15 minutes</option>
                <option>30 minutes</option>
                <option>1 hour</option>
              </select>
            </div>
          </div>
        </div>
      </div>

      <div className="dashboard-card">
        <h3>Recent Security Events</h3>
        <DataTable 
          columns={['Event', 'User', 'IP Address', 'Time', 'Status']}
          data={[
            ['Failed Login Attempt', 'admin@lms.com', '192.168.1.100', '2 mins ago', <span className="badge badge-danger">Blocked</span>],
            ['Suspicious Activity Detected', 'student@lms.com', '192.168.1.105', '1 hour ago', <span className="badge badge-warning">Flagged</span>],
            ['Password Changed', 'mentor@lms.com', '192.168.1.102', '3 hours ago', <span className="badge badge-success">Success</span>]
          ]}
        />
      </div>
    </div>
  );
};

// Continue with Student Pages in next file due to length...
// STUDENT PAGES (DETAILED - SPECIAL ATTENTION)

const StudentDashboard = () => {
  return (
    <div className="page-wrapper">
      <div className="page-header">
        <h1 className="page-title">Welcome back, Student! 👋</h1>
        <p className="page-subtitle">Your learning journey at a glance</p>
      </div>

      <div className="stats-grid">
        <StatCard icon="📚" label="Enrolled Courses" value="4" trend="1 in progress" color="blue" />
        <StatCard icon="✅" label="Completed Tasks" value="23" trend="↑ 5 this week" color="green" />
        <StatCard icon="🎯" label="Overall Progress" value="68%" trend="↑ 12% this month" color="purple" />
        <StatCard icon="🏆" label="Certificates Earned" value="2" trend="Keep learning!" color="orange" />
      </div>

      <div className="dashboard-grid">
        <div className="dashboard-card card-span-2">
          <div className="card-header">
            <h3>Continue Learning</h3>
            <a href="#" className="btn-text">View All</a>
          </div>
          <div className="courses-grid-compact">
            {[
              { title: 'React Masterclass', progress: 75, image: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)' },
              { title: 'Python for Data Science', progress: 45, image: 'linear-gradient(135deg, #f093fb 0%, #f5576c 100%)' },
              { title: 'UI/UX Design Fundamentals', progress: 60, image: 'linear-gradient(135deg, #4facfe 0%, #00f2fe 100%)' }
            ].map((course, i) => (
              <CourseCard key={i} {...course} instructor="Instructor Name" />
            ))}
          </div>
        </div>

        <div className="dashboard-card">
          <div className="card-header">
            <h3>Upcoming Deadlines</h3>
          </div>
          <div className="deadline-list">
            {[
              { task: 'React Assignment #5', course: 'React Masterclass', due: '2 days', urgent: true },
              { task: 'Python Quiz', course: 'Python Course', due: '4 days', urgent: false },
              { task: 'Design Project', course: 'UI/UX Design', due: '1 week', urgent: false }
            ].map((item, i) => (
              <div key={i} className={`deadline-item ${item.urgent ? 'urgent' : ''}`}>
                <div className="deadline-icon">{item.urgent ? '⚠️' : '📝'}</div>
                <div className="deadline-content">
                  <p className="deadline-title">{item.task}</p>
                  <p className="deadline-course">{item.course}</p>
                </div>
                <span className="deadline-time">Due in {item.due}</span>
              </div>
            ))}
          </div>
          <button className="btn-link">View All Tasks →</button>
        </div>
      </div>

      <div className="dashboard-card">
        <div className="card-header">
          <h3>Your Progress Overview</h3>
          <select className="filter-select-sm">
            <option>This Month</option>
            <option>Last 3 Months</option>
          </select>
        </div>
        <div className="progress-overview">
          {[
            { course: 'React Masterclass', completed: 15, total: 20, progress: 75 },
            { course: 'Python for Data Science', completed: 9, total: 20, progress: 45 },
            { course: 'UI/UX Design', completed: 12, total: 20, progress: 60 },
            { course: 'Data Structures', completed: 5, total: 20, progress: 25 }
          ].map((item, i) => (
            <div key={i} className="progress-item">
              <div className="progress-header">
                <span className="progress-course">{item.course}</span>
                <span className="progress-stats">{item.completed}/{item.total} modules</span>
              </div>
              <div className="progress-bar-large">
                <div className="progress-fill" style={{ width: `${item.progress}%` }}></div>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};

const CoursesList = () => {
  return (
    <div className="page-wrapper">
      <div className="page-header">
        <div>
          <h1 className="page-title">Browse Courses</h1>
          <p className="page-subtitle">Discover and enroll in new courses</p>
        </div>
      </div>

      <SearchFilter 
        filters={[
          { label: 'Category', options: ['All', 'Programming', 'Design', 'Business', 'Data Science'] },
          { label: 'Level', options: ['All', 'Beginner', 'Intermediate', 'Advanced'] },
          { label: 'Duration', options: ['All', 'Short (< 4 weeks)', 'Medium (4-8 weeks)', 'Long (> 8 weeks)'] }
        ]}
      />

      <div className="category-tabs">
        {['All Courses', 'Programming', 'Design', 'Business', 'Data Science', 'Marketing'].map((cat, i) => (
          <button key={i} className={`category-tab ${i === 0 ? 'active' : ''}`}>{cat}</button>
        ))}
      </div>

      <div className="courses-grid">
        {[
          { title: 'Complete React Developer Course', instructor: 'Sarah Johnson', students: 450, image: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)', category: 'Programming', duration: '12 weeks', level: 'Intermediate' },
          { title: 'Python for Data Science', instructor: 'Mike Chen', students: 380, image: 'linear-gradient(135deg, #f093fb 0%, #f5576c 100%)', category: 'Data Science', duration: '10 weeks', level: 'Beginner' },
          { title: 'UI/UX Design Fundamentals', instructor: 'Emily Davis', students: 520, image: 'linear-gradient(135deg, #4facfe 0%, #00f2fe 100%)', category: 'Design', duration: '8 weeks', level: 'Beginner' },
          { title: 'Advanced JavaScript Patterns', instructor: 'John Smith', students: 290, image: 'linear-gradient(135deg, #fa709a 0%, #fee140 100%)', category: 'Programming', duration: '6 weeks', level: 'Advanced' },
          { title: 'Machine Learning A-Z', instructor: 'Dr. Alan Roberts', students: 610, image: 'linear-gradient(135deg, #30cfd0 0%, #330867 100%)', category: 'Data Science', duration: '14 weeks', level: 'Advanced' },
          { title: 'Figma for Beginners', instructor: 'Lisa Wong', students: 340, image: 'linear-gradient(135deg, #a8edea 0%, #fed6e3 100%)', category: 'Design', duration: '4 weeks', level: 'Beginner' }
        ].map((course, i) => (
          <div key={i} className="course-card course-card-hover">
            <CourseCard {...course} />
            <div className="course-footer">
              <button className="btn-primary btn-block">Enroll Now</button>
            </div>
          </div>
        ))}
      </div>

      <div className="pagination">
        <button className="btn-secondary">← Previous</button>
        <div className="pagination-numbers">
          <button className="page-btn active">1</button>
          <button className="page-btn">2</button>
          <button className="page-btn">3</button>
          <button className="page-btn">4</button>
        </div>
        <button className="btn-secondary">Next →</button>
      </div>
    </div>
  );
};

const RegisteredCourses = () => {
  return (
    <div className="page-wrapper">
      <div className="page-header">
        <h1 className="page-title">My Enrolled Courses</h1>
        <p className="page-subtitle">Continue your learning journey</p>
      </div>

      <div className="view-toggle">
        <button className="view-btn active">⊞ Grid</button>
        <button className="view-btn">☰ List</button>
      </div>

      <div className="courses-grid">
        {[
          { title: 'React Masterclass', instructor: 'Sarah Johnson', progress: 75, image: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)', nextLesson: 'Module 15: Advanced Hooks', timeSpent: '32 hours' },
          { title: 'Python for Data Science', instructor: 'Mike Chen', progress: 45, image: 'linear-gradient(135deg, #f093fb 0%, #f5576c 100%)', nextLesson: 'Module 9: Pandas Library', timeSpent: '18 hours' },
          { title: 'UI/UX Design Fundamentals', instructor: 'Emily Davis', progress: 60, image: 'linear-gradient(135deg, #4facfe 0%, #00f2fe 100%)', nextLesson: 'Module 12: Prototyping', timeSpent: '24 hours' },
          { title: 'Data Structures & Algorithms', instructor: 'John Smith', progress: 25, image: 'linear-gradient(135deg, #fa709a 0%, #fee140 100%)', nextLesson: 'Module 5: Binary Trees', timeSpent: '12 hours' }
        ].map((course, i) => (
          <div key={i} className="enrolled-course-card">
            <div className="course-image" style={{ background: course.image }}>
              <div className="course-progress-overlay">
                <div className="circular-progress">
                  <span className="progress-percent">{course.progress}%</span>
                </div>
              </div>
            </div>
            <div className="course-body">
              <h3 className="course-title">{course.title}</h3>
              <p className="course-instructor">👨‍🏫 {course.instructor}</p>
              <div className="course-stats">
                <span className="stat-chip">⏱️ {course.timeSpent}</span>
                <span className="stat-chip">🎯 {course.progress}% complete</span>
              </div>
              <div className="next-lesson">
                <p className="next-lesson-label">Next Lesson:</p>
                <p className="next-lesson-title">{course.nextLesson}</p>
              </div>
              <button className="btn-primary btn-block">Continue Learning →</button>
            </div>
          </div>
        ))}
      </div>

      <div className="dashboard-card">
        <h3>Learning Statistics</h3>
        <div className="stats-grid">
          <div className="stat-box">
            <div className="stat-icon-large">📊</div>
            <h4>Total Study Time</h4>
            <p className="stat-large">86 hours</p>
            <p className="stat-subtext">This month: 24 hours</p>
          </div>
          <div className="stat-box">
            <div className="stat-icon-large">✅</div>
            <h4>Completed Modules</h4>
            <p className="stat-large">41</p>
            <p className="stat-subtext">9 this week</p>
          </div>
          <div className="stat-box">
            <div className="stat-icon-large">🔥</div>
            <h4>Learning Streak</h4>
            <p className="stat-large">12 days</p>
            <p className="stat-subtext">Keep it up!</p>
          </div>
          <div className="stat-box">
            <div className="stat-icon-large">🎯</div>
            <h4>Avg. Score</h4>
            <p className="stat-large">87%</p>
            <p className="stat-subtext">Excellent performance</p>
          </div>
        </div>
      </div>
    </div>
  );
};

const TaskSubmission = () => {
  const [selectedFiles, setSelectedFiles] = useState([]);
  
  return (
    <div className="page-wrapper">
      <div className="page-header">
        <h1 className="page-title">Task Submission</h1>
        <p className="page-subtitle">Submit assignments and track your submissions</p>
      </div>

      <div className="tabs-container">
        <div className="tabs">
          <button className="tab active">Pending <span className="tab-count">3</span></button>
          <button className="tab">Submitted <span className="tab-count">15</span></button>
          <button className="tab">Graded <span className="tab-count">12</span></button>
        </div>
      </div>

      <div className="task-list">
        {[
          { title: 'React Hooks Assignment', course: 'React Masterclass', due: '2 days', points: 100, urgent: true },
          { title: 'Python Project Submission', course: 'Python for Data Science', due: '5 days', points: 150, urgent: false },
          { title: 'Design Wireframes', course: 'UI/UX Design', due: '1 week', points: 80, urgent: false }
        ].map((task, i) => (
          <div key={i} className={`task-card ${task.urgent ? 'task-urgent' : ''}`}>
            <div className="task-header">
              <div>
                <h3>{task.title}</h3>
                <p className="text-muted">{task.course} • {task.points} points</p>
              </div>
              <div className="task-meta">
                {task.urgent && <span className="badge badge-danger">Urgent</span>}
                <span className="due-badge">Due in {task.due}</span>
              </div>
            </div>
            <div className="task-body">
              <p className="task-description">
                Complete the assignment following the guidelines provided in the course materials. 
                Make sure to include all required files and documentation.
              </p>
              <div className="task-requirements">
                <h4>Requirements:</h4>
                <ul>
                  <li>✓ Source code files</li>
                  <li>✓ Documentation (README.md)</li>
                  <li>✓ Screenshots or demo video</li>
                </ul>
              </div>
            </div>
            <div className="task-actions">
              <button className="btn-secondary">📄 View Instructions</button>
              <button className="btn-primary">📤 Submit Assignment</button>
            </div>
          </div>
        ))}
      </div>

      <div className="dashboard-card">
        <h3>Submit New Assignment</h3>
        <form className="submission-form">
          <div className="form-group">
            <label>Select Assignment</label>
            <select>
              <option>React Hooks Assignment</option>
              <option>Python Project Submission</option>
              <option>Design Wireframes</option>
            </select>
          </div>
          
          <div className="form-group">
            <label>Assignment Notes</label>
            <textarea rows="4" placeholder="Add any notes or comments for your instructor..."></textarea>
          </div>

          <div className="form-group">
            <label>Upload Files</label>
            <div className="file-upload-area">
              <div className="file-upload-icon">📎</div>
              <p>Drag and drop files here or click to browse</p>
              <input type="file" multiple hidden />
              <button type="button" className="btn-secondary">Choose Files</button>
            </div>
            {selectedFiles.length > 0 && (
              <div className="uploaded-files">
                {selectedFiles.map((file, i) => (
                  <div key={i} className="file-chip">
                    📄 {file.name}
                    <button className="file-remove">✕</button>
                  </div>
                ))}
              </div>
            )}
          </div>

          <button type="submit" className="btn-primary">Submit Assignment</button>
        </form>
      </div>
    </div>
  );
};

const AttendanceView = () => {
  return (
    <div className="page-wrapper">
      <div className="page-header">
        <h1 className="page-title">My Attendance</h1>
        <p className="page-subtitle">Track your attendance records</p>
      </div>

      <div className="stats-grid">
        <StatCard icon="✅" label="Total Classes" value="48" trend="This semester" color="blue" />
        <StatCard icon="👍" label="Attended" value="42" trend="87.5%" color="green" />
        <StatCard icon="❌" label="Missed" value="6" trend="12.5%" color="red" />
        <StatCard icon="📊" label="Attendance Rate" value="87.5%" trend="Good standing" color="purple" />
      </div>

      <div className="dashboard-card">
        <div className="card-header">
          <h3>Attendance Calendar</h3>
          <div className="month-selector">
            <button className="btn-icon">←</button>
            <span>January 2024</span>
            <button className="btn-icon">→</button>
          </div>
        </div>
        <div className="attendance-calendar">
          <div className="calendar-legend">
            <span className="legend-item"><span className="legend-dot present"></span> Present</span>
            <span className="legend-item"><span className="legend-dot absent"></span> Absent</span>
            <span className="legend-item"><span className="legend-dot holiday"></span> Holiday</span>
          </div>
          <div className="calendar-grid">
            {['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'].map((day, i) => (
              <div key={i} className="calendar-day-header">{day}</div>
            ))}
            {[...Array(31)].map((_, i) => {
              const status = i % 7 === 0 ? 'holiday' : i % 8 === 0 ? 'absent' : 'present';
              return (
                <div key={i} className={`calendar-day attendance-${status}`}>
                  <span className="day-number">{i+1}</span>
                </div>
              );
            })}
          </div>
        </div>
      </div>

      <div className="dashboard-card">
        <div className="card-header">
          <h3>Course-wise Attendance</h3>
        </div>
        <div className="course-attendance-list">
          {[
            { course: 'React Masterclass', attended: 15, total: 16, percentage: 94 },
            { course: 'Python for Data Science', attended: 12, total: 14, percentage: 86 },
            { course: 'UI/UX Design', attended: 10, total: 12, percentage: 83 },
            { course: 'Data Structures', attended: 5, total: 6, percentage: 83 }
          ].map((item, i) => (
            <div key={i} className="course-attendance-item">
              <div className="course-attendance-header">
                <h4>{item.course}</h4>
                <span className={`attendance-percentage ${item.percentage >= 90 ? 'excellent' : item.percentage >= 75 ? 'good' : 'warning'}`}>
                  {item.percentage}%
                </span>
              </div>
              <div className="attendance-stats">
                <span>{item.attended} attended • {item.total - item.attended} missed • {item.total} total</span>
              </div>
              <div className="progress-bar">
                <div className="progress-fill" style={{ width: `${item.percentage}%` }}></div>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};

const Certificates = () => {
  return (
    <div className="page-wrapper">
      <div className="page-header">
        <h1 className="page-title">My Certificates</h1>
        <p className="page-subtitle">Your earned certificates and achievements</p>
      </div>

      <div className="certificates-grid">
        {[
          { title: 'React Masterclass', issueDate: 'December 2023', score: '95%', id: 'CERT-2023-001' },
          { title: 'Python Basics', issueDate: 'November 2023', score: '88%', id: 'CERT-2023-002' }
        ].map((cert, i) => (
          <div key={i} className="certificate-card">
            <div className="certificate-badge">
              <div className="badge-ribbon">🏆</div>
              <p className="certificate-title">{cert.title}</p>
            </div>
            <div className="certificate-details">
              <div className="detail-row">
                <span className="detail-label">Certificate ID:</span>
                <span className="detail-value">{cert.id}</span>
              </div>
              <div className="detail-row">
                <span className="detail-label">Issue Date:</span>
                <span className="detail-value">{cert.issueDate}</span>
              </div>
              <div className="detail-row">
                <span className="detail-label">Final Score:</span>
                <span className="detail-value">{cert.score}</span>
              </div>
            </div>
            <div className="certificate-actions">
              <button className="btn-secondary">👁️ View</button>
              <button className="btn-primary">⬇️ Download</button>
              <button className="btn-secondary">🔗 Share</button>
            </div>
          </div>
        ))}

        <div className="certificate-card certificate-locked">
          <div className="locked-content">
            <div className="lock-icon">🔒</div>
            <h3>UI/UX Design Course</h3>
            <p>Complete the course to unlock this certificate</p>
            <div className="progress-bar">
              <div className="progress-fill" style={{ width: '60%' }}></div>
            </div>
            <span className="progress-text">60% Complete</span>
          </div>
        </div>

        <div className="certificate-card certificate-locked">
          <div className="locked-content">
            <div className="lock-icon">🔒</div>
            <h3>Data Structures</h3>
            <p>Complete the course to unlock this certificate</p>
            <div className="progress-bar">
              <div className="progress-fill" style={{ width: '25%' }}></div>
            </div>
            <span className="progress-text">25% Complete</span>
          </div>
        </div>
      </div>

      <div className="dashboard-card">
        <h3>Achievement Stats</h3>
        <div className="achievement-stats">
          <div className="achievement-item">
            <div className="achievement-icon">🎯</div>
            <div className="achievement-content">
              <h4>2 Certificates Earned</h4>
              <p>Keep learning to unlock more</p>
            </div>
          </div>
          <div className="achievement-item">
            <div className="achievement-icon">📈</div>
            <div className="achievement-content">
              <h4>Average Score: 91.5%</h4>
              <p>Excellent performance!</p>
            </div>
          </div>
          <div className="achievement-item">
            <div className="achievement-icon">⭐</div>
            <div className="achievement-content">
              <h4>Skills Mastered: 12</h4>
              <p>React, Python, Design and more</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

// Mentor Pages (Continued from Admin/Student)
const MentorDashboard = () => (
  <div className="page-wrapper">
    <div className="page-header">
      <h1 className="page-title">Mentor Dashboard</h1>
      <p className="page-subtitle">Your teaching overview and quick actions</p>
    </div>
    <div className="stats-grid">
      <StatCard icon="📚" label="Active Courses" value="5" trend="2 new this month" color="blue" />
      <StatCard icon="👥" label="Total Students" value="287" trend="↑ 45 this month" color="green" />
      <StatCard icon="📝" label="Pending Tasks" value="12" trend="Needs review" color="orange" />
      <StatCard icon="⭐" label="Avg. Rating" value="4.8" trend="Excellent!" color="purple" />
    </div>
    <div className="coming-soon-banner">
      <span className="placeholder-icon">🚧</span>
      <p>Detailed mentor dashboard coming soon...</p>
    </div>
  </div>
);

const MentorCourses = () => (
  <div className="page-wrapper">
    <div className="page-header">
      <h1 className="page-title">My Courses</h1>
      <p className="page-subtitle">View and edit your courses</p>
    </div>
    <div className="coming-soon-banner">
      <span className="placeholder-icon">🚧</span>
      <p>Course management interface coming soon...</p>
    </div>
  </div>
);

const VideoSessions = () => (
  <div className="page-wrapper">
    <div className="page-header">
      <h1 className="page-title">Video Sessions</h1>
      <p className="page-subtitle">Zoom/Teams integration for live classes</p>
    </div>
    <div className="coming-soon-banner">
      <span className="placeholder-icon">🚧</span>
      <p>Video session integration coming soon...</p>
    </div>
  </div>
);

const TaskAssignment = () => (
  <div className="page-wrapper">
    <div className="page-header">
      <h1 className="page-title">Task Assignment</h1>
      <p className="page-subtitle">Create and assign tasks to students</p>
    </div>
    <div className="coming-soon-banner">
      <span className="placeholder-icon">🚧</span>
      <p>Task assignment interface coming soon...</p>
    </div>
  </div>
);

const AttendanceManagement = () => (
  <div className="page-wrapper">
    <div className="page-header">
      <h1 className="page-title">Attendance Management</h1>
      <p className="page-subtitle">Track student attendance</p>
    </div>
    <div className="coming-soon-banner">
      <span className="placeholder-icon">🚧</span>
      <p>Attendance management coming soon...</p>
    </div>
  </div>
);

const ProgressTracking = () => (
  <div className="page-wrapper">
    <div className="page-header">
      <h1 className="page-title">Progress Tracking</h1>
      <p className="page-subtitle">Monitor student progress</p>
    </div>
    <div className="coming-soon-banner">
      <span className="placeholder-icon">🚧</span>
      <p>Progress tracking interface coming soon...</p>
    </div>
  </div>
);

const MaterialsUpload = () => (
  <div className="page-wrapper">
    <div className="page-header">
      <h1 className="page-title">Materials Upload</h1>
      <p className="page-subtitle">Upload course materials and resources</p>
    </div>
    <div className="coming-soon-banner">
      <span className="placeholder-icon">🚧</span>
      <p>Materials upload interface coming soon...</p>
    </div>
  </div>
);

const CertificateGeneration = () => (
  <div className="page-wrapper">
    <div className="page-header">
      <h1 className="page-title">Certificate Generation</h1>
      <p className="page-subtitle">Generate certificates for students</p>
    </div>
    <div className="coming-soon-banner">
      <span className="placeholder-icon">🚧</span>
      <p>Certificate generation coming soon...</p>
    </div>
  </div>
);

// Menu Items
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
          <Route path="/login" element={<LoginPage />} />
          <Route path="/register" element={<RegisterPage />} />
          
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
          
          <Route path="/" element={<Navigate to="/login" />} />
        </Routes>
      </AuthProvider>
    </Router>
  );
}

export default App;