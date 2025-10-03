import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { useAuth } from '../../contexts/AuthContext';
import * as mockService from '../../services/mockService';

const StatCard = ({ icon, label, value, trend, color = 'blue' }) => (
  <motion.div 
    className={`bg-white dark:bg-gray-800 rounded-xl shadow-lg p-6 border-l-4 ${
      color === 'blue' ? 'border-blue-500' :
      color === 'green' ? 'border-green-500' :
      color === 'orange' ? 'border-orange-500' :
      color === 'purple' ? 'border-purple-500' : 'border-gray-500'
    }`}
    whileHover={{ scale: 1.02 }}
    transition={{ duration: 0.2 }}
  >
    <div className="flex items-center justify-between">
      <div className="flex-1">
        <p className="text-sm font-medium text-gray-600 dark:text-gray-400">{label}</p>
        <p className="text-3xl font-bold text-gray-900 dark:text-white mt-2">{value}</p>
        {trend && <p className="text-sm text-gray-500 dark:text-gray-400 mt-1">{trend}</p>}
      </div>
      <div className="text-4xl">{icon}</div>
    </div>
  </motion.div>
);

const NotificationItem = ({ icon, title, message, time, type }) => (
  <div className={`flex items-start space-x-3 p-3 rounded-lg hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors ${
    type === 'urgent' ? 'bg-red-50 dark:bg-red-900/20' : ''
  }`}>
    <div className="text-2xl">{icon}</div>
    <div className="flex-1 min-w-0">
      <p className="text-sm font-medium text-gray-900 dark:text-white">{title}</p>
      <p className="text-sm text-gray-600 dark:text-gray-400 truncate">{message}</p>
      <p className="text-xs text-gray-500 dark:text-gray-500 mt-1">{time}</p>
    </div>
  </div>
);

const RecentActivityItem = ({ activity, course, time, icon }) => (
  <div className="flex items-center space-x-3 p-3 border-b border-gray-200 dark:border-gray-700 last:border-0">
    <div className="text-xl">{icon}</div>
    <div className="flex-1">
      <p className="text-sm text-gray-900 dark:text-white">{activity}</p>
      <p className="text-xs text-gray-500 dark:text-gray-400">{course}</p>
    </div>
    <span className="text-xs text-gray-500 dark:text-gray-400">{time}</span>
  </div>
);

const MentorDashboardMain = () => {
  const { user } = useAuth();
  const [stats, setStats] = useState({
    activeCourses: 0,
    totalStudents: 0,
    pendingTasks: 0,
    avgRating: 0
  });
  const [notifications, setNotifications] = useState([]);
  const [recentActivity, setRecentActivity] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadDashboardData();
  }, []);

  const loadDashboardData = async () => {
    try {
      setLoading(true);
      
      // Fetch mentor's courses
      const courses = await mockService.getCourses({ instructor_id: user?.id });
      const activeCourses = courses.filter(c => c.status === 'active');
      
      // Calculate total students
      const totalStudents = activeCourses.reduce((sum, course) => sum + (course.total_students || 0), 0);
      
      // Fetch pending task submissions
      const tasks = await mockService.getTasks({ instructor_id: user?.id });
      const submissions = await mockService.getSubmissions({ status: 'pending' });
      
      // Calculate average rating
      const avgRating = activeCourses.length > 0
        ? (activeCourses.reduce((sum, course) => sum + (course.rating || 0), 0) / activeCourses.length).toFixed(1)
        : '0.0';
      
      setStats({
        activeCourses: activeCourses.length,
        totalStudents,
        pendingTasks: submissions.length,
        avgRating
      });
      
      // Mock notifications
      setNotifications([
        {
          icon: '🔔',
          title: 'New Submission',
          message: '5 students submitted React Assignment',
          time: '10 mins ago',
          type: 'normal'
        },
        {
          icon: '⚠️',
          title: 'Low Attendance Alert',
          message: '3 students below 75% attendance',
          time: '1 hour ago',
          type: 'urgent'
        },
        {
          icon: '📝',
          title: 'Task Due Soon',
          message: 'JavaScript Quiz deadline tomorrow',
          time: '2 hours ago',
          type: 'normal'
        },
        {
          icon: '⭐',
          title: 'New Review',
          message: 'Student rated your course 5 stars',
          time: '3 hours ago',
          type: 'normal'
        }
      ]);
      
      // Mock recent activity
      setRecentActivity([
        { activity: 'Graded 5 assignments', course: 'React Masterclass', time: '30m ago', icon: '✅' },
        { activity: 'Updated course materials', course: 'Node.js Backend', time: '2h ago', icon: '📚' },
        { activity: 'Marked attendance', course: 'React Masterclass', time: '5h ago', icon: '📋' },
        { activity: 'Created new task', course: 'Advanced JavaScript', time: '1d ago', icon: '➕' },
        { activity: 'Sent certificate', course: 'React Masterclass', time: '2d ago', icon: '🏆' }
      ]);
    } catch (error) {
      console.error('Error loading dashboard data:', error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="p-6 space-y-6">
        <div className="animate-pulse space-y-6">
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
            {[...Array(4)].map((_, i) => (
              <div key={i} className="h-32 bg-gray-200 dark:bg-gray-700 rounded-xl"></div>
            ))}
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="p-6 space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-3xl font-bold text-gray-900 dark:text-white">Mentor Dashboard</h1>
        <p className="text-gray-600 dark:text-gray-400 mt-1">
          Welcome back, {user?.full_name || 'Mentor'}! Here's your teaching overview.
        </p>
      </div>

      {/* Stats Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <StatCard 
          icon="📚" 
          label="Active Courses" 
          value={stats.activeCourses} 
          trend={`${stats.activeCourses} courses running`}
          color="blue" 
        />
        <StatCard 
          icon="👥" 
          label="Total Students" 
          value={stats.totalStudents} 
          trend="Across all courses"
          color="green" 
        />
        <StatCard 
          icon="📝" 
          label="Pending Tasks" 
          value={stats.pendingTasks} 
          trend="Needs review"
          color="orange" 
        />
        <StatCard 
          icon="⭐" 
          label="Avg. Rating" 
          value={stats.avgRating} 
          trend="Excellent performance!"
          color="purple" 
        />
      </div>

      {/* Main Content Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Notifications Panel */}
        <div className="lg:col-span-2">
          <div className="bg-white dark:bg-gray-800 rounded-xl shadow-lg p-6">
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-xl font-bold text-gray-900 dark:text-white">Notifications</h2>
              <button className="text-sm text-blue-600 dark:text-blue-400 hover:underline">
                View All
              </button>
            </div>
            <div className="space-y-2">
              {notifications.map((notif, index) => (
                <NotificationItem key={index} {...notif} />
              ))}
            </div>
          </div>
        </div>

        {/* Recent Activity */}
        <div className="lg:col-span-1">
          <div className="bg-white dark:bg-gray-800 rounded-xl shadow-lg p-6">
            <h2 className="text-xl font-bold text-gray-900 dark:text-white mb-4">Recent Activity</h2>
            <div className="space-y-1">
              {recentActivity.map((activity, index) => (
                <RecentActivityItem key={index} {...activity} />
              ))}
            </div>
          </div>
        </div>
      </div>

      {/* Quick Actions */}
      <div className="bg-gradient-to-r from-blue-500 to-purple-600 rounded-xl shadow-lg p-6 text-white">
        <h2 className="text-xl font-bold mb-4">Quick Actions</h2>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <button className="bg-white/20 hover:bg-white/30 transition-colors rounded-lg p-4 text-center">
            <div className="text-3xl mb-2">➕</div>
            <div className="text-sm font-medium">Create Task</div>
          </button>
          <button className="bg-white/20 hover:bg-white/30 transition-colors rounded-lg p-4 text-center">
            <div className="text-3xl mb-2">✓</div>
            <div className="text-sm font-medium">Mark Attendance</div>
          </button>
          <button className="bg-white/20 hover:bg-white/30 transition-colors rounded-lg p-4 text-center">
            <div className="text-3xl mb-2">📤</div>
            <div className="text-sm font-medium">Upload Material</div>
          </button>
          <button className="bg-white/20 hover:bg-white/30 transition-colors rounded-lg p-4 text-center">
            <div className="text-3xl mb-2">📊</div>
            <div className="text-sm font-medium">View Reports</div>
          </button>
        </div>
      </div>
    </div>
  );
};

export default MentorDashboardMain;