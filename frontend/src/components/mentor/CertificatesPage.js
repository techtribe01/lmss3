import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { useAuth } from '../../contexts/AuthContext';
import { useToast } from '../../hooks/use-toast';
import * as mockService from '../../services/mockService';
import { Button } from '../ui/button';
import { Input } from '../ui/input';
import { Label } from '../ui/label';

const CertificateCard = ({ certificate }) => (
  <motion.div
    initial={{ opacity: 0, y: 20 }}
    animate={{ opacity: 1, y: 0 }}
    className="bg-white dark:bg-gray-800 rounded-lg shadow-lg p-6 hover:shadow-xl transition-shadow"
  >
    <div className="flex items-start gap-4">
      <div className="text-5xl">🏆</div>
      <div className="flex-1">
        <h3 className="text-lg font-bold text-gray-900 dark:text-white">
          {certificate.student_name}
        </h3>
        <p className="text-sm text-gray-600 dark:text-gray-400 mt-1">
          {certificate.course_name}
        </p>
        <div className="flex items-center gap-4 mt-3 text-xs text-gray-500 dark:text-gray-400">
          <span>📅 Issued: {new Date(certificate.issued_date).toLocaleDateString()}</span>
          <span className={`px-2 py-1 rounded-full ${
            certificate.status === 'issued' 
              ? 'bg-green-100 text-green-800 dark:bg-green-900/30 dark:text-green-400'
              : 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900/30 dark:text-yellow-400'
          }`}>
            {certificate.status}
          </span>
        </div>
      </div>
    </div>
    
    <div className="flex gap-2 mt-4">
      <Button variant="outline" className="flex-1" size="sm">
        👁️ Preview
      </Button>
      <Button variant="outline" className="flex-1" size="sm">
        ⬇️ Download
      </Button>
      <Button variant="outline" className="flex-1" size="sm">
        📧 Email
      </Button>
    </div>
  </motion.div>
);

const GenerateCertificateModal = ({ onClose, onGenerate, courses }) => {
  const { toast } = useToast();
  const [formData, setFormData] = useState({
    course_id: '',
    student_ids: []
  });
  const [students, setStudents] = useState([]);
  const [selectedStudents, setSelectedStudents] = useState(new Set());
  const [generating, setGenerating] = useState(false);

  useEffect(() => {
    if (formData.course_id) {
      loadStudents();
    }
  }, [formData.course_id]);

  const loadStudents = async () => {
    try {
      // In real app, fetch enrolled students for the course
      const enrollments = await mockService.getEnrollments({ course_id: formData.course_id });
      const studentPromises = enrollments.map(e => mockService.getUserById(e.student_id));
      const studentsData = await Promise.all(studentPromises);
      setStudents(studentsData.filter(s => s));
    } catch (error) {
      console.error('Error loading students:', error);
    }
  };

  const toggleStudent = (studentId) => {
    const newSelected = new Set(selectedStudents);
    if (newSelected.has(studentId)) {
      newSelected.delete(studentId);
    } else {
      newSelected.add(studentId);
    }
    setSelectedStudents(newSelected);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (selectedStudents.size === 0) {
      toast({
        title: 'Error',
        description: 'Please select at least one student',
        variant: 'destructive'
      });
      return;
    }
    
    setGenerating(true);
    
    try {
      // Simulate certificate generation
      await new Promise(resolve => setTimeout(resolve, 2000));
      
      toast({
        title: 'Success',
        description: `Generated ${selectedStudents.size} certificate(s) successfully!`
      });
      onGenerate();
      onClose();
    } catch (error) {
      toast({
        title: 'Error',
        description: 'Failed to generate certificates',
        variant: 'destructive'
      });
    } finally {
      setGenerating(false);
    }
  };

  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      exit={{ opacity: 0 }}
      className="fixed inset-0 bg-black/50 flex items-center justify-center p-4 z-50"
      onClick={onClose}
    >
      <motion.div
        initial={{ scale: 0.9, opacity: 0 }}
        animate={{ scale: 1, opacity: 1 }}
        exit={{ scale: 0.9, opacity: 0 }}
        className="bg-white dark:bg-gray-800 rounded-xl shadow-2xl max-w-2xl w-full max-h-[90vh] overflow-y-auto"
        onClick={(e) => e.stopPropagation()}
      >
        <div className="sticky top-0 bg-white dark:bg-gray-800 border-b border-gray-200 dark:border-gray-700 p-6 z-10">
          <h2 className="text-2xl font-bold text-gray-900 dark:text-white">Generate Certificate</h2>
        </div>
        
        <form onSubmit={handleSubmit} className="p-6 space-y-4">
          <div className="space-y-2">
            <Label htmlFor="course_id">Select Course *</Label>
            <select
              id="course_id"
              value={formData.course_id}
              onChange={(e) => setFormData({ ...formData, course_id: e.target.value })}
              className="flex h-9 w-full rounded-md border border-input bg-white dark:bg-gray-800 px-3 py-1 text-base text-gray-900 dark:text-gray-100 shadow-sm focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-blue-500"
              required
            >
              <option value="">Choose a course...</option>
              {courses.map(course => (
                <option key={course.id} value={course.id}>{course.title}</option>
              ))}
            </select>
          </div>

          {formData.course_id && students.length > 0 && (
            <div className="space-y-2">
              <Label>Select Students *</Label>
              <div className="border border-gray-200 dark:border-gray-700 rounded-lg max-h-64 overflow-y-auto">
                {students.map((student) => (
                  <div
                    key={student.id}
                    className="flex items-center gap-3 p-3 hover:bg-gray-50 dark:hover:bg-gray-700/50 border-b border-gray-200 dark:border-gray-700 last:border-0 cursor-pointer"
                    onClick={() => toggleStudent(student.id)}
                  >
                    <input
                      type="checkbox"
                      checked={selectedStudents.has(student.id)}
                      onChange={() => {}}
                      className="w-4 h-4 text-blue-600 rounded"
                    />
                    <div className="flex-1">
                      <p className="text-sm font-medium text-gray-900 dark:text-white">
                        {student.full_name}
                      </p>
                      <p className="text-xs text-gray-600 dark:text-gray-400">
                        {student.email}
                      </p>
                    </div>
                  </div>
                ))}
              </div>
              <p className="text-xs text-gray-500 dark:text-gray-400">
                {selectedStudents.size} student(s) selected
              </p>
            </div>
          )}

          {formData.course_id && students.length === 0 && (
            <div className="text-center py-8 text-gray-600 dark:text-gray-400">
              No students enrolled in this course
            </div>
          )}

          <div className="flex gap-3 pt-4">
            <Button
              type="button"
              onClick={onClose}
              variant="outline"
              className="flex-1"
              disabled={generating}
            >
              Cancel
            </Button>
            <Button
              type="submit"
              className="flex-1 bg-gradient-to-r from-blue-600 to-purple-600 hover:opacity-90"
              disabled={generating || !formData.course_id || selectedStudents.size === 0}
            >
              {generating ? '⏳ Generating...' : '🏆 Generate Certificates'}
            </Button>
          </div>
        </form>
      </motion.div>
    </motion.div>
  );
};

const CertificatesPage = () => {
  const { user } = useAuth();
  const [certificates, setCertificates] = useState([]);
  const [courses, setCourses] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showGenerateModal, setShowGenerateModal] = useState(false);
  const [filterCourse, setFilterCourse] = useState('all');

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    try {
      setLoading(true);
      
      // Load courses
      const coursesData = await mockService.getCourses({ instructor_id: user?.id });
      setCourses(coursesData);
      
      // Mock certificates data
      const students = await mockService.getUsers('student');
      const mockCertificates = students.slice(0, 5).map((student, index) => ({
        id: `cert-${index}`,
        student_id: student.id,
        student_name: student.full_name,
        course_id: coursesData[index % coursesData.length]?.id,
        course_name: coursesData[index % coursesData.length]?.title,
        issued_date: new Date(Date.now() - 86400000 * (index + 1) * 7).toISOString(),
        status: index % 3 === 0 ? 'pending' : 'issued'
      }));
      
      setCertificates(mockCertificates);
    } catch (error) {
      console.error('Error loading data:', error);
    } finally {
      setLoading(false);
    }
  };

  const filteredCertificates = filterCourse === 'all' 
    ? certificates 
    : certificates.filter(c => c.course_id === filterCourse);

  if (loading) {
    return (
      <div className="p-6">
        <div className="animate-pulse space-y-6">
          <div className="h-12 bg-gray-200 dark:bg-gray-700 rounded w-1/3"></div>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {[...Array(4)].map((_, i) => (
              <div key={i} className="h-40 bg-gray-200 dark:bg-gray-700 rounded-lg"></div>
            ))}
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="p-6 space-y-6">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4">
        <div>
          <h1 className="text-3xl font-bold text-gray-900 dark:text-white">Certificate Generation</h1>
          <p className="text-gray-600 dark:text-gray-400 mt-1">
            Generate and manage student certificates
          </p>
        </div>
        <Button 
          onClick={() => setShowGenerateModal(true)}
          className="bg-gradient-to-r from-blue-600 to-purple-600 hover:opacity-90"
        >
          🏆 Generate Certificate
        </Button>
      </div>

      {/* Filter */}
      {courses.length > 0 && (
        <div className="bg-white dark:bg-gray-800 rounded-lg shadow-lg p-4">
          <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
            Filter by Course
          </label>
          <select
            value={filterCourse}
            onChange={(e) => setFilterCourse(e.target.value)}
            className="w-full md:w-96 rounded-md border border-input bg-white dark:bg-gray-800 px-3 py-2 text-gray-900 dark:text-gray-100 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-blue-500"
          >
            <option value="all">All Courses</option>
            {courses.map(course => (
              <option key={course.id} value={course.id}>{course.title}</option>
            ))}
          </select>
        </div>
      )}

      {/* Certificates Grid */}
      {filteredCertificates.length === 0 ? (
        <div className="text-center py-12">
          <div className="text-6xl mb-4">🏆</div>
          <h3 className="text-xl font-semibold text-gray-900 dark:text-white mb-2">
            No certificates yet
          </h3>
          <p className="text-gray-600 dark:text-gray-400 mb-4">
            Generate your first certificate to get started
          </p>
          <Button 
            onClick={() => setShowGenerateModal(true)}
            className="bg-gradient-to-r from-blue-600 to-purple-600 hover:opacity-90"
          >
            Generate Certificate
          </Button>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {filteredCertificates.map((certificate) => (
            <CertificateCard key={certificate.id} certificate={certificate} />
          ))}
        </div>
      )}

      {/* Generate Modal */}
      <AnimatePresence>
        {showGenerateModal && (
          <GenerateCertificateModal
            onClose={() => setShowGenerateModal(false)}
            onGenerate={loadData}
            courses={courses}
          />
        )}
      </AnimatePresence>
    </div>
  );
};

export default CertificatesPage;