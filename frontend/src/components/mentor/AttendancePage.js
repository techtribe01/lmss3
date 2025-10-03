import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { useAuth } from '../../contexts/AuthContext';
import { useToast } from '../../hooks/use-toast';
import * as mockService from '../../services/mockService';
import { Button } from '../ui/button';

const AttendancePage = () => {
  const { user } = useAuth();
  const { toast } = useToast();
  const [courses, setCourses] = useState([]);
  const [selectedCourse, setSelectedCourse] = useState(null);
  const [students, setStudents] = useState([]);
  const [attendance, setAttendance] = useState({});
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [lastUpdate, setLastUpdate] = useState(Date.now());

  useEffect(() => {
    loadCourses();
  }, []);

  useEffect(() => {
    if (selectedCourse) {
      loadStudents();
    }
  }, [selectedCourse]);

  // Polling for real-time updates every 5 seconds
  useEffect(() => {
    if (selectedCourse) {
      const interval = setInterval(() => {
        loadStudents();
        setLastUpdate(Date.now());
      }, 5000);
      return () => clearInterval(interval);
    }
  }, [selectedCourse]);

  const loadCourses = async () => {
    try {
      setLoading(true);
      const data = await mockService.getCourses({ instructor_id: user?.id, status: 'active' });
      setCourses(data);
      if (data.length > 0) {
        setSelectedCourse(data[0].id);
      }
    } catch (error) {
      console.error('Error loading courses:', error);
    } finally {
      setLoading(false);
    }
  };

  const loadStudents = async () => {
    try {
      const enrollments = await mockService.getEnrollments({ course_id: selectedCourse });
      const studentPromises = enrollments.map(e => mockService.getUserById(e.student_id));
      const studentsData = await Promise.all(studentPromises);
      
      setStudents(studentsData.filter(s => s));
      
      // Initialize attendance state
      const today = new Date().toISOString().split('T')[0];
      const attendanceRecords = await mockService.getAttendance({ 
        course_id: selectedCourse,
        date: today
      });
      
      const attendanceMap = {};
      studentsData.forEach(student => {
        const record = attendanceRecords.find(a => a.student_id === student.id);
        attendanceMap[student.id] = record ? record.status : 'absent';
      });
      
      setAttendance(attendanceMap);
    } catch (error) {
      console.error('Error loading students:', error);
    }
  };

  const toggleAttendance = (studentId) => {
    setAttendance(prev => ({
      ...prev,
      [studentId]: prev[studentId] === 'present' ? 'absent' : 'present'
    }));
  };

  const saveAttendance = async () => {
    setSaving(true);
    try {
      const today = new Date().toISOString().split('T')[0];
      
      for (const [studentId, status] of Object.entries(attendance)) {
        await mockService.markAttendance({
          student_id: studentId,
          course_id: selectedCourse,
          date: today,
          status
        });
      }
      
      toast({
        title: 'Success',
        description: 'Attendance saved successfully!'
      });
    } catch (error) {
      toast({
        title: 'Error',
        description: 'Failed to save attendance',
        variant: 'destructive'
      });
    } finally {
      setSaving(false);
    }
  };

  if (loading) {
    return (
      <div className="p-6">
        <div className="animate-pulse space-y-6">
          <div className="h-12 bg-gray-200 dark:bg-gray-700 rounded w-1/3"></div>
          <div className="h-64 bg-gray-200 dark:bg-gray-700 rounded"></div>
        </div>
      </div>
    );
  }

  return (
    <div className="p-6 space-y-6">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4">
        <div>
          <h1 className="text-3xl font-bold text-gray-900 dark:text-white">Attendance Management</h1>
          <p className="text-gray-600 dark:text-gray-400 mt-1">
            Track student attendance in real-time
          </p>
          <p className="text-xs text-gray-500 dark:text-gray-500 mt-1">
            🔄 Last updated: {new Date(lastUpdate).toLocaleTimeString()}
          </p>
        </div>
        <Button 
          onClick={saveAttendance}
          disabled={saving || students.length === 0}
          className="bg-gradient-to-r from-blue-600 to-purple-600 hover:opacity-90"
        >
          {saving ? 'Saving...' : '💾 Save Attendance'}
        </Button>
      </div>

      {/* Course Selection */}
      {courses.length > 0 && (
        <div className="bg-white dark:bg-gray-800 rounded-lg shadow-lg p-4">
          <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
            Select Course
          </label>
          <select
            value={selectedCourse || ''}
            onChange={(e) => setSelectedCourse(e.target.value)}
            className="w-full md:w-96 rounded-md border border-input bg-white dark:bg-gray-800 px-3 py-2 text-gray-900 dark:text-gray-100 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-blue-500"
          >
            {courses.map(course => (
              <option key={course.id} value={course.id}>{course.title}</option>
            ))}
          </select>
        </div>
      )}

      {/* Attendance Table */}
      {students.length === 0 ? (
        <div className="text-center py-12">
          <div className="text-6xl mb-4">👥</div>
          <h3 className="text-xl font-semibold text-gray-900 dark:text-white mb-2">
            No students enrolled
          </h3>
          <p className="text-gray-600 dark:text-gray-400">
            Students will appear here once they enroll in this course
          </p>
        </div>
      ) : (
        <div className="bg-white dark:bg-gray-800 rounded-lg shadow-lg overflow-hidden">
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead className="bg-gray-50 dark:bg-gray-700">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
                    Student Name
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
                    Email
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
                    Attendance %
                  </th>
                  <th className="px-6 py-3 text-center text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
                    Status
                  </th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-200 dark:divide-gray-700">
                {students.map((student) => (
                  <motion.tr 
                    key={student.id}
                    initial={{ opacity: 0 }}
                    animate={{ opacity: 1 }}
                    className="hover:bg-gray-50 dark:hover:bg-gray-700/50 transition-colors"
                  >
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="text-sm font-medium text-gray-900 dark:text-white">
                        {student.full_name}
                      </div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="text-sm text-gray-600 dark:text-gray-400">
                        {student.email}
                      </div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="text-sm text-gray-900 dark:text-white">
                        {student.attendance_percentage || 0}%
                      </div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-center">
                      <button
                        onClick={() => toggleAttendance(student.id)}
                        className={`px-4 py-2 rounded-full text-sm font-medium transition-colors ${
                          attendance[student.id] === 'present'
                            ? 'bg-green-100 text-green-800 dark:bg-green-900/30 dark:text-green-400 hover:bg-green-200 dark:hover:bg-green-900/50'
                            : 'bg-red-100 text-red-800 dark:bg-red-900/30 dark:text-red-400 hover:bg-red-200 dark:hover:bg-red-900/50'
                        }`}
                      >
                        {attendance[student.id] === 'present' ? '✓ Present' : '✗ Absent'}
                      </button>
                    </td>
                  </motion.tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* Summary */}
      {students.length > 0 && (
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6 text-center">
            <p className="text-3xl font-bold text-blue-600 dark:text-blue-400">
              {students.length}
            </p>
            <p className="text-sm text-gray-600 dark:text-gray-400 mt-1">Total Students</p>
          </div>
          <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6 text-center">
            <p className="text-3xl font-bold text-green-600 dark:text-green-400">
              {Object.values(attendance).filter(s => s === 'present').length}
            </p>
            <p className="text-sm text-gray-600 dark:text-gray-400 mt-1">Present Today</p>
          </div>
          <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6 text-center">
            <p className="text-3xl font-bold text-red-600 dark:text-red-400">
              {Object.values(attendance).filter(s => s === 'absent').length}
            </p>
            <p className="text-sm text-gray-600 dark:text-gray-400 mt-1">Absent Today</p>
          </div>
        </div>
      )}
    </div>
  );
};

export default AttendancePage;