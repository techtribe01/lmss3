import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { useAuth } from '../../contexts/AuthContext';
import * as mockService from '../../services/mockService';

const ProgressBar = ({ value, max, color = 'blue' }) => {
  const percentage = (value / max) * 100;
  const colorClass = {
    blue: 'bg-blue-600',
    green: 'bg-green-600',
    yellow: 'bg-yellow-600',
    red: 'bg-red-600',
    purple: 'bg-purple-600'
  }[color] || 'bg-blue-600';

  return (
    <div className="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-2">
      <motion.div
        className={`${colorClass} h-2 rounded-full`}
        initial={{ width: 0 }}
        animate={{ width: `${percentage}%` }}
        transition={{ duration: 0.5 }}
      />
    </div>
  );
};

const StudentProgressCard = ({ student }) => {
  const getPerformanceColor = (percentage) => {
    if (percentage >= 90) return 'green';
    if (percentage >= 75) return 'blue';
    if (percentage >= 60) return 'yellow';
    return 'red';
  };

  const overallProgress = Math.round(
    (student.completed_tasks / student.total_tasks) * 100
  );

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className="bg-white dark:bg-gray-800 rounded-lg shadow-lg p-6"
    >
      <div className="flex items-start justify-between mb-4">
        <div>
          <h3 className="text-lg font-bold text-gray-900 dark:text-white">
            {student.full_name}
          </h3>
          <p className="text-sm text-gray-600 dark:text-gray-400">{student.email}</p>
        </div>
        <div className={`px-3 py-1 rounded-full text-xs font-medium ${
          overallProgress >= 75 
            ? 'bg-green-100 text-green-800 dark:bg-green-900/30 dark:text-green-400'
            : overallProgress >= 50
            ? 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900/30 dark:text-yellow-400'
            : 'bg-red-100 text-red-800 dark:bg-red-900/30 dark:text-red-400'
        }`}>
          {overallProgress}% Complete
        </div>
      </div>

      <div className="space-y-4">
        {/* Attendance */}
        <div>
          <div className="flex justify-between text-sm mb-1">
            <span className="text-gray-600 dark:text-gray-400">Attendance</span>
            <span className="font-semibold text-gray-900 dark:text-white">
              {student.attendance_percentage}%
            </span>
          </div>
          <ProgressBar 
            value={student.attendance_percentage} 
            max={100} 
            color={getPerformanceColor(student.attendance_percentage)}
          />
        </div>

        {/* Tasks Completed */}
        <div>
          <div className="flex justify-between text-sm mb-1">
            <span className="text-gray-600 dark:text-gray-400">Tasks Completed</span>
            <span className="font-semibold text-gray-900 dark:text-white">
              {student.completed_tasks}/{student.total_tasks}
            </span>
          </div>
          <ProgressBar 
            value={student.completed_tasks} 
            max={student.total_tasks} 
            color="purple"
          />
        </div>

        {/* Course Progress */}
        <div>
          <div className="flex justify-between text-sm mb-1">
            <span className="text-gray-600 dark:text-gray-400">Courses</span>
            <span className="font-semibold text-gray-900 dark:text-white">
              {student.completed_courses}/{student.enrolled_courses}
            </span>
          </div>
          <ProgressBar 
            value={student.completed_courses} 
            max={student.enrolled_courses} 
            color="blue"
          />
        </div>
      </div>

      <div className="mt-4 pt-4 border-t border-gray-200 dark:border-gray-700">
        <div className="grid grid-cols-3 gap-4 text-center">
          <div>
            <p className="text-xs text-gray-600 dark:text-gray-400">Enrolled</p>
            <p className="text-lg font-bold text-gray-900 dark:text-white">
              {student.enrolled_courses}
            </p>
          </div>
          <div>
            <p className="text-xs text-gray-600 dark:text-gray-400">Completed</p>
            <p className="text-lg font-bold text-green-600 dark:text-green-400">
              {student.completed_courses}
            </p>
          </div>
          <div>
            <p className="text-xs text-gray-600 dark:text-gray-400">In Progress</p>
            <p className="text-lg font-bold text-blue-600 dark:text-blue-400">
              {student.enrolled_courses - student.completed_courses}
            </p>
          </div>
        </div>
      </div>
    </motion.div>
  );
};

const ProgressTrackingPage = () => {
  const { user } = useAuth();
  const [students, setStudents] = useState([]);
  const [courses, setCourses] = useState([]);
  const [selectedCourse, setSelectedCourse] = useState('all');
  const [loading, setLoading] = useState(true);
  const [stats, setStats] = useState({
    avgAttendance: 0,
    avgTaskCompletion: 0,
    topPerformers: 0,
    needsAttention: 0
  });

  useEffect(() => {
    loadData();
  }, []);

  useEffect(() => {
    if (students.length > 0) {
      calculateStats();
    }
  }, [students]);

  const loadData = async () => {
    try {
      setLoading(true);
      
      // Load mentor's courses
      const coursesData = await mockService.getCourses({ instructor_id: user?.id });
      setCourses(coursesData);
      
      // Load students (mock data for now)
      const studentsData = await mockService.getUsers('student');
      setStudents(studentsData);
    } catch (error) {
      console.error('Error loading data:', error);
    } finally {
      setLoading(false);
    }
  };

  const calculateStats = () => {
    const avgAttendance = Math.round(
      students.reduce((sum, s) => sum + (s.attendance_percentage || 0), 0) / students.length
    );
    
    const avgTaskCompletion = Math.round(
      students.reduce((sum, s) => sum + ((s.completed_tasks / s.total_tasks) * 100 || 0), 0) / students.length
    );
    
    const topPerformers = students.filter(
      s => s.attendance_percentage >= 90 && (s.completed_tasks / s.total_tasks) >= 0.9
    ).length;
    
    const needsAttention = students.filter(
      s => s.attendance_percentage < 75 || (s.completed_tasks / s.total_tasks) < 0.5
    ).length;
    
    setStats({ avgAttendance, avgTaskCompletion, topPerformers, needsAttention });
  };

  if (loading) {
    return (
      <div className="p-6">
        <div className="animate-pulse space-y-6">
          <div className="h-12 bg-gray-200 dark:bg-gray-700 rounded w-1/3"></div>
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
        <h1 className="text-3xl font-bold text-gray-900 dark:text-white">Progress Tracking</h1>
        <p className="text-gray-600 dark:text-gray-400 mt-1">
          Monitor student performance and progress
        </p>
      </div>

      {/* Stats Overview */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <div className="bg-white dark:bg-gray-800 rounded-xl shadow-lg p-6 border-l-4 border-blue-500">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600 dark:text-gray-400">Avg Attendance</p>
              <p className="text-3xl font-bold text-gray-900 dark:text-white mt-2">
                {stats.avgAttendance}%
              </p>
            </div>
            <div className="text-4xl">📊</div>
          </div>
        </div>

        <div className="bg-white dark:bg-gray-800 rounded-xl shadow-lg p-6 border-l-4 border-purple-500">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600 dark:text-gray-400">Avg Task Completion</p>
              <p className="text-3xl font-bold text-gray-900 dark:text-white mt-2">
                {stats.avgTaskCompletion}%
              </p>
            </div>
            <div className="text-4xl">✅</div>
          </div>
        </div>

        <div className="bg-white dark:bg-gray-800 rounded-xl shadow-lg p-6 border-l-4 border-green-500">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600 dark:text-gray-400">Top Performers</p>
              <p className="text-3xl font-bold text-gray-900 dark:text-white mt-2">
                {stats.topPerformers}
              </p>
            </div>
            <div className="text-4xl">⭐</div>
          </div>
        </div>

        <div className="bg-white dark:bg-gray-800 rounded-xl shadow-lg p-6 border-l-4 border-red-500">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600 dark:text-gray-400">Needs Attention</p>
              <p className="text-3xl font-bold text-gray-900 dark:text-white mt-2">
                {stats.needsAttention}
              </p>
            </div>
            <div className="text-4xl">⚠️</div>
          </div>
        </div>
      </div>

      {/* Course Filter */}
      {courses.length > 0 && (
        <div className="bg-white dark:bg-gray-800 rounded-lg shadow-lg p-4">
          <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
            Filter by Course
          </label>
          <select
            value={selectedCourse}
            onChange={(e) => setSelectedCourse(e.target.value)}
            className="w-full md:w-96 rounded-md border border-input bg-white dark:bg-gray-800 px-3 py-2 text-gray-900 dark:text-gray-100 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-blue-500"
          >
            <option value="all">All Courses</option>
            {courses.map(course => (
              <option key={course.id} value={course.id}>{course.title}</option>
            ))}
          </select>
        </div>
      )}

      {/* Student Progress Cards */}
      {students.length === 0 ? (
        <div className="text-center py-12">
          <div className="text-6xl mb-4">📈</div>
          <h3 className="text-xl font-semibold text-gray-900 dark:text-white mb-2">
            No student data available
          </h3>
          <p className="text-gray-600 dark:text-gray-400">
            Student progress will appear here once they start courses
          </p>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {students.map((student) => (
            <StudentProgressCard key={student.id} student={student} />
          ))}
        </div>
      )}
    </div>
  );
};

export default ProgressTrackingPage;