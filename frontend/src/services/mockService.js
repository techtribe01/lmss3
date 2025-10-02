// Mock Service Layer for CRUD operations
// This simulates backend API calls with in-memory storage

import {
  mockUsers,
  mockCourses,
  mockBatches,
  mockAttendance,
  mockGrades,
  mockTasks,
  mockSubmissions,
  mockEnrollments,
  mockCertificates
} from './mockData';

// In-memory storage (resets on page reload)
let users = [...mockUsers];
let courses = [...mockCourses];
let batches = [...mockBatches];
let attendance = [...mockAttendance];
let grades = [...mockGrades];
let tasks = [...mockTasks];
let submissions = [...mockSubmissions];
let enrollments = [...mockEnrollments];
let certificates = [...mockCertificates];

// Helper function to simulate API delay
const delay = (ms = 300) => new Promise(resolve => setTimeout(resolve, ms));

// Helper to generate unique ID
const generateId = (prefix) => `${prefix}-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;

// ============ USER OPERATIONS ============
export const getUsers = async (role = null) => {
  await delay();
  if (role) {
    return users.filter(u => u.role === role);
  }
  return users;
};

export const getUserById = async (id) => {
  await delay();
  return users.find(u => u.id === id);
};

export const updateUser = async (id, updates) => {
  await delay();
  const index = users.findIndex(u => u.id === id);
  if (index !== -1) {
    users[index] = { ...users[index], ...updates };
    return users[index];
  }
  throw new Error('User not found');
};

export const deleteUser = async (id) => {
  await delay();
  users = users.filter(u => u.id !== id);
  return { success: true };
};

// ============ COURSE OPERATIONS ============
export const getCourses = async (filters = {}) => {
  await delay();
  let filtered = [...courses];
  
  if (filters.category && filters.category !== 'All') {
    filtered = filtered.filter(c => c.category === filters.category);
  }
  if (filters.level && filters.level !== 'All') {
    filtered = filtered.filter(c => c.level === filters.level);
  }
  if (filters.status && filters.status !== 'All') {
    filtered = filtered.filter(c => c.status === filters.status);
  }
  if (filters.instructor_id) {
    filtered = filtered.filter(c => c.instructor_id === filters.instructor_id);
  }
  if (filters.search) {
    const searchLower = filters.search.toLowerCase();
    filtered = filtered.filter(c => 
      c.title.toLowerCase().includes(searchLower) ||
      c.description.toLowerCase().includes(searchLower)
    );
  }
  
  return filtered;
};

export const getCourseById = async (id) => {
  await delay();
  return courses.find(c => c.id === id);
};

export const createCourse = async (courseData) => {
  await delay();
  const newCourse = {
    id: generateId('course'),
    ...courseData,
    total_students: 0,
    status: courseData.status || 'draft',
    created_at: new Date().toISOString()
  };
  courses.push(newCourse);
  return newCourse;
};

export const updateCourse = async (id, updates) => {
  await delay();
  const index = courses.findIndex(c => c.id === id);
  if (index !== -1) {
    courses[index] = { ...courses[index], ...updates };
    return courses[index];
  }
  throw new Error('Course not found');
};

export const deleteCourse = async (id) => {
  await delay();
  courses = courses.filter(c => c.id !== id);
  // Also remove related batches
  batches = batches.filter(b => b.course_id !== id);
  return { success: true };
};

// ============ BATCH OPERATIONS ============
export const getBatches = async (filters = {}) => {
  await delay();
  let filtered = [...batches];
  
  if (filters.course_id) {
    filtered = filtered.filter(b => b.course_id === filters.course_id);
  }
  if (filters.mentor_id) {
    filtered = filtered.filter(b => b.mentor_id === filters.mentor_id);
  }
  if (filters.status && filters.status !== 'All') {
    filtered = filtered.filter(b => b.status === filters.status);
  }
  
  return filtered;
};

export const getBatchById = async (id) => {
  await delay();
  return batches.find(b => b.id === id);
};

export const createBatch = async (batchData) => {
  await delay();
  const newBatch = {
    id: generateId('batch'),
    ...batchData,
    total_students: 0,
    created_at: new Date().toISOString()
  };
  batches.push(newBatch);
  return newBatch;
};

export const updateBatch = async (id, updates) => {
  await delay();
  const index = batches.findIndex(b => b.id === id);
  if (index !== -1) {
    batches[index] = { ...batches[index], ...updates };
    return batches[index];
  }
  throw new Error('Batch not found');
};

export const deleteBatch = async (id) => {
  await delay();
  batches = batches.filter(b => b.id !== id);
  return { success: true };
};

// ============ ATTENDANCE OPERATIONS ============
export const getAttendance = async (filters = {}) => {
  await delay();
  let filtered = [...attendance];
  
  if (filters.batch_id) {
    filtered = filtered.filter(a => a.batch_id === filters.batch_id);
  }
  if (filters.student_id) {
    filtered = filtered.filter(a => a.student_id === filters.student_id);
  }
  if (filters.date) {
    filtered = filtered.filter(a => a.date === filters.date);
  }
  
  return filtered;
};

export const markAttendance = async (attendanceData) => {
  await delay();
  const newAttendance = {
    id: generateId('attend'),
    ...attendanceData,
    created_at: new Date().toISOString()
  };
  attendance.push(newAttendance);
  return newAttendance;
};

export const bulkMarkAttendance = async (attendanceList) => {
  await delay();
  const newRecords = attendanceList.map(data => ({
    id: generateId('attend'),
    ...data,
    created_at: new Date().toISOString()
  }));
  attendance.push(...newRecords);
  return newRecords;
};

export const updateAttendance = async (id, updates) => {
  await delay();
  const index = attendance.findIndex(a => a.id === id);
  if (index !== -1) {
    attendance[index] = { ...attendance[index], ...updates };
    return attendance[index];
  }
  throw new Error('Attendance record not found');
};

// ============ GRADE OPERATIONS ============
export const getGrades = async (filters = {}) => {
  await delay();
  let filtered = [...grades];
  
  if (filters.course_id) {
    filtered = filtered.filter(g => g.course_id === filters.course_id);
  }
  if (filters.student_id) {
    filtered = filtered.filter(g => g.student_id === filters.student_id);
  }
  if (filters.assessment_type) {
    filtered = filtered.filter(g => g.assessment_type === filters.assessment_type);
  }
  
  return filtered;
};

export const createGrade = async (gradeData) => {
  await delay();
  const newGrade = {
    id: generateId('grade'),
    ...gradeData,
    graded_at: new Date().toISOString()
  };
  grades.push(newGrade);
  return newGrade;
};

export const updateGrade = async (id, updates) => {
  await delay();
  const index = grades.findIndex(g => g.id === id);
  if (index !== -1) {
    grades[index] = { ...grades[index], ...updates };
    return grades[index];
  }
  throw new Error('Grade not found');
};

// ============ TASK OPERATIONS ============
export const getTasks = async (filters = {}) => {
  await delay();
  let filtered = [...tasks];
  
  if (filters.course_id) {
    filtered = filtered.filter(t => t.course_id === filters.course_id);
  }
  if (filters.batch_id) {
    filtered = filtered.filter(t => t.batch_id === filters.batch_id);
  }
  if (filters.status && filters.status !== 'All') {
    filtered = filtered.filter(t => t.status === filters.status);
  }
  
  return filtered;
};

export const getTaskById = async (id) => {
  await delay();
  return tasks.find(t => t.id === id);
};

export const createTask = async (taskData) => {
  await delay();
  const newTask = {
    id: generateId('task'),
    ...taskData,
    total_submissions: 0,
    pending_submissions: 0,
    created_at: new Date().toISOString()
  };
  tasks.push(newTask);
  return newTask;
};

export const updateTask = async (id, updates) => {
  await delay();
  const index = tasks.findIndex(t => t.id === id);
  if (index !== -1) {
    tasks[index] = { ...tasks[index], ...updates };
    return tasks[index];
  }
  throw new Error('Task not found');
};

export const deleteTask = async (id) => {
  await delay();
  tasks = tasks.filter(t => t.id !== id);
  // Also remove related submissions
  submissions = submissions.filter(s => s.task_id !== id);
  return { success: true };
};

// ============ SUBMISSION OPERATIONS ============
export const getSubmissions = async (filters = {}) => {
  await delay();
  let filtered = [...submissions];
  
  if (filters.task_id) {
    filtered = filtered.filter(s => s.task_id === filters.task_id);
  }
  if (filters.student_id) {
    filtered = filtered.filter(s => s.student_id === filters.student_id);
  }
  if (filters.status && filters.status !== 'All') {
    filtered = filtered.filter(s => s.status === filters.status);
  }
  
  return filtered;
};

export const submitTask = async (submissionData) => {
  await delay();
  const newSubmission = {
    id: generateId('sub'),
    ...submissionData,
    status: 'pending',
    score: null,
    feedback: null,
    graded_by: null,
    graded_at: null,
    submitted_at: new Date().toISOString()
  };
  submissions.push(newSubmission);
  return newSubmission;
};

export const gradeSubmission = async (id, gradeData) => {
  await delay();
  const index = submissions.findIndex(s => s.id === id);
  if (index !== -1) {
    submissions[index] = {
      ...submissions[index],
      ...gradeData,
      status: 'graded',
      graded_at: new Date().toISOString()
    };
    return submissions[index];
  }
  throw new Error('Submission not found');
};

// ============ ENROLLMENT OPERATIONS ============
export const getEnrollments = async (filters = {}) => {
  await delay();
  let filtered = [...enrollments];
  
  if (filters.student_id) {
    filtered = filtered.filter(e => e.student_id === filters.student_id);
  }
  if (filters.course_id) {
    filtered = filtered.filter(e => e.course_id === filters.course_id);
  }
  if (filters.status && filters.status !== 'All') {
    filtered = filtered.filter(e => e.status === filters.status);
  }
  
  return filtered;
};

export const enrollStudent = async (enrollmentData) => {
  await delay();
  const newEnrollment = {
    id: generateId('enroll'),
    ...enrollmentData,
    progress: 0,
    status: 'active',
    enrolled_at: new Date().toISOString()
  };
  enrollments.push(newEnrollment);
  
  // Update course student count
  const courseIndex = courses.findIndex(c => c.id === enrollmentData.course_id);
  if (courseIndex !== -1) {
    courses[courseIndex].total_students += 1;
  }
  
  return newEnrollment;
};

export const updateEnrollment = async (id, updates) => {
  await delay();
  const index = enrollments.findIndex(e => e.id === id);
  if (index !== -1) {
    enrollments[index] = { ...enrollments[index], ...updates };
    return enrollments[index];
  }
  throw new Error('Enrollment not found');
};

// ============ CERTIFICATE OPERATIONS ============
export const getCertificates = async (filters = {}) => {
  await delay();
  let filtered = [...certificates];
  
  if (filters.student_id) {
    filtered = filtered.filter(c => c.student_id === filters.student_id);
  }
  if (filters.course_id) {
    filtered = filtered.filter(c => c.course_id === filters.course_id);
  }
  
  return filtered;
};

export const issueCertificate = async (certificateData) => {
  await delay();
  const newCertificate = {
    id: generateId('cert'),
    ...certificateData,
    issued_date: new Date().toISOString().split('T')[0],
    certificate_url: `/certificates/${generateId('cert')}.pdf`
  };
  certificates.push(newCertificate);
  return newCertificate;
};

// ============ STATISTICS & ANALYTICS ============
export const getDashboardStats = async (role, userId) => {
  await delay();
  
  if (role === 'admin') {
    return {
      total_students: users.filter(u => u.role === 'student').length,
      total_mentors: users.filter(u => u.role === 'mentor').length,
      total_courses: courses.length,
      active_courses: courses.filter(c => c.status === 'active').length,
      total_batches: batches.length,
      pending_approvals: courses.filter(c => c.status === 'pending_approval').length
    };
  }
  
  if (role === 'mentor') {
    const mentorCourses = courses.filter(c => c.instructor_id === userId);
    const mentorBatches = batches.filter(b => b.mentor_id === userId);
    const mentorTasks = tasks.filter(t => t.assigned_by === userId);
    
    return {
      total_courses: mentorCourses.length,
      total_students: mentorCourses.reduce((sum, c) => sum + c.total_students, 0),
      total_batches: mentorBatches.length,
      pending_submissions: mentorTasks.reduce((sum, t) => sum + t.pending_submissions, 0)
    };
  }
  
  if (role === 'student') {
    const studentEnrollments = enrollments.filter(e => e.student_id === userId);
    const studentSubmissions = submissions.filter(s => s.student_id === userId);
    const studentCertificates = certificates.filter(c => c.student_id === userId);
    
    return {
      enrolled_courses: studentEnrollments.filter(e => e.status === 'active').length,
      completed_courses: studentEnrollments.filter(e => e.status === 'completed').length,
      pending_tasks: studentSubmissions.filter(s => s.status === 'pending').length,
      certificates_earned: studentCertificates.length
    };
  }
  
  return {};
};

// Reset function (useful for testing)
export const resetMockData = () => {
  users = [...mockUsers];
  courses = [...mockCourses];
  batches = [...mockBatches];
  attendance = [...mockAttendance];
  grades = [...mockGrades];
  tasks = [...mockTasks];
  submissions = [...mockSubmissions];
  enrollments = [...mockEnrollments];
  certificates = [...mockCertificates];
};
