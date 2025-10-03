import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { useAuth } from '../../contexts/AuthContext';
import { useToast } from '../../hooks/use-toast';
import * as mockService from '../../services/mockService';
import { Button } from '../ui/button';
import { Input } from '../ui/input';
import { Label } from '../ui/label';
import { Textarea } from '../ui/textarea';

const CourseCard = ({ course, onEdit }) => (
  <motion.div
    initial={{ opacity: 0, y: 20 }}
    animate={{ opacity: 1, y: 0 }}
    className="bg-white dark:bg-gray-800 rounded-xl shadow-lg overflow-hidden hover:shadow-xl transition-shadow"
  >
    <div 
      className="h-48 flex items-center justify-center text-white font-bold text-2xl"
      style={{ background: course.image || 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)' }}
    >
      {course.title}
    </div>
    <div className="p-6">
      <div className="flex items-start justify-between mb-4">
        <div>
          <h3 className="text-xl font-bold text-gray-900 dark:text-white">{course.title}</h3>
          <p className="text-sm text-gray-600 dark:text-gray-400 mt-1">{course.category} • {course.level}</p>
        </div>
        <span className={`px-3 py-1 rounded-full text-xs font-medium ${
          course.status === 'active' ? 'bg-green-100 text-green-800 dark:bg-green-900/30 dark:text-green-400' :
          course.status === 'pending_approval' ? 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900/30 dark:text-yellow-400' :
          'bg-gray-100 text-gray-800 dark:bg-gray-700 dark:text-gray-400'
        }`}>
          {course.status}
        </span>
      </div>
      
      <p className="text-gray-600 dark:text-gray-400 text-sm mb-4 line-clamp-2">
        {course.description}
      </p>
      
      <div className="grid grid-cols-3 gap-4 mb-4">
        <div className="text-center">
          <p className="text-2xl font-bold text-blue-600 dark:text-blue-400">{course.total_students}</p>
          <p className="text-xs text-gray-600 dark:text-gray-400">Students</p>
        </div>
        <div className="text-center">
          <p className="text-2xl font-bold text-green-600 dark:text-green-400">{course.total_lessons}</p>
          <p className="text-xs text-gray-600 dark:text-gray-400">Lessons</p>
        </div>
        <div className="text-center">
          <p className="text-2xl font-bold text-purple-600 dark:text-purple-400">{course.rating || 'N/A'}</p>
          <p className="text-xs text-gray-600 dark:text-gray-400">Rating</p>
        </div>
      </div>
      
      <Button 
        onClick={() => onEdit(course)} 
        className="w-full bg-gradient-to-r from-blue-600 to-purple-600 hover:opacity-90"
      >
        Edit Course
      </Button>
    </div>
  </motion.div>
);

const EditCourseModal = ({ course, onClose, onSave }) => {
  const { toast } = useToast();
  const [formData, setFormData] = useState({
    title: course.title || '',
    description: course.description || '',
    category: course.category || '',
    level: course.level || '',
    duration: course.duration || '',
    price: course.price || 0,
    zoom_link: course.zoom_link || '',
    teams_link: course.teams_link || ''
  });
  const [saving, setSaving] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setSaving(true);
    
    try {
      await mockService.updateCourse(course.id, formData);
      toast({
        title: 'Success',
        description: 'Course updated successfully!'
      });
      onSave();
      onClose();
    } catch (error) {
      toast({
        title: 'Error',
        description: 'Failed to update course',
        variant: 'destructive'
      });
    } finally {
      setSaving(false);
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
          <h2 className="text-2xl font-bold text-gray-900 dark:text-white">Edit Course</h2>
        </div>
        
        <form onSubmit={handleSubmit} className="p-6 space-y-4">
          <div className="space-y-2">
            <Label htmlFor="title">Course Title *</Label>
            <Input
              id="title"
              value={formData.title}
              onChange={(e) => setFormData({ ...formData, title: e.target.value })}
              required
            />
          </div>

          <div className="space-y-2">
            <Label htmlFor="description">Description *</Label>
            <Textarea
              id="description"
              value={formData.description}
              onChange={(e) => setFormData({ ...formData, description: e.target.value })}
              rows={4}
              required
            />
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div className="space-y-2">
              <Label htmlFor="category">Category</Label>
              <Input
                id="category"
                value={formData.category}
                onChange={(e) => setFormData({ ...formData, category: e.target.value })}
              />
            </div>
            
            <div className="space-y-2">
              <Label htmlFor="level">Level</Label>
              <select
                id="level"
                value={formData.level}
                onChange={(e) => setFormData({ ...formData, level: e.target.value })}
                className="flex h-9 w-full rounded-md border border-input bg-white dark:bg-gray-800 px-3 py-1 text-base text-gray-900 dark:text-gray-100 shadow-sm focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-blue-500"
              >
                <option value="Beginner">Beginner</option>
                <option value="Intermediate">Intermediate</option>
                <option value="Advanced">Advanced</option>
              </select>
            </div>
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div className="space-y-2">
              <Label htmlFor="duration">Duration</Label>
              <Input
                id="duration"
                value={formData.duration}
                onChange={(e) => setFormData({ ...formData, duration: e.target.value })}
                placeholder="e.g., 8 weeks"
              />
            </div>
            
            <div className="space-y-2">
              <Label htmlFor="price">Price ($)</Label>
              <Input
                id="price"
                type="number"
                value={formData.price}
                onChange={(e) => setFormData({ ...formData, price: parseFloat(e.target.value) })}
              />
            </div>
          </div>

          <div className="border-t border-gray-200 dark:border-gray-700 pt-4 mt-4">
            <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
              Video Session Integration
            </h3>
            
            <div className="space-y-4">
              <div className="space-y-2">
                <Label htmlFor="zoom_link">
                  <span className="flex items-center gap-2">
                    <span className="text-2xl">🎥</span>
                    Zoom Meeting Link
                  </span>
                </Label>
                <Input
                  id="zoom_link"
                  type="url"
                  value={formData.zoom_link}
                  onChange={(e) => setFormData({ ...formData, zoom_link: e.target.value })}
                  placeholder="https://zoom.us/j/..."
                />
                <p className="text-xs text-gray-500 dark:text-gray-400">
                  Add your Zoom meeting link for live sessions
                </p>
              </div>

              <div className="space-y-2">
                <Label htmlFor="teams_link">
                  <span className="flex items-center gap-2">
                    <span className="text-2xl">💼</span>
                    Microsoft Teams Link
                  </span>
                </Label>
                <Input
                  id="teams_link"
                  type="url"
                  value={formData.teams_link}
                  onChange={(e) => setFormData({ ...formData, teams_link: e.target.value })}
                  placeholder="https://teams.microsoft.com/..."
                />
                <p className="text-xs text-gray-500 dark:text-gray-400">
                  Add your Teams meeting link for live sessions
                </p>
              </div>
            </div>
          </div>

          <div className="flex gap-3 pt-4">
            <Button
              type="button"
              onClick={onClose}
              variant="outline"
              className="flex-1"
              disabled={saving}
            >
              Cancel
            </Button>
            <Button
              type="submit"
              className="flex-1 bg-gradient-to-r from-blue-600 to-purple-600 hover:opacity-90"
              disabled={saving}
            >
              {saving ? 'Saving...' : 'Save Changes'}
            </Button>
          </div>
        </form>
      </motion.div>
    </motion.div>
  );
};

const MentorCoursesPage = () => {
  const { user } = useAuth();
  const [courses, setCourses] = useState([]);
  const [loading, setLoading] = useState(true);
  const [editingCourse, setEditingCourse] = useState(null);
  const [searchTerm, setSearchTerm] = useState('');

  useEffect(() => {
    loadCourses();
  }, []);

  const loadCourses = async () => {
    try {
      setLoading(true);
      const data = await mockService.getCourses({ instructor_id: user?.id });
      setCourses(data);
    } catch (error) {
      console.error('Error loading courses:', error);
    } finally {
      setLoading(false);
    }
  };

  const filteredCourses = courses.filter(course =>
    course.title.toLowerCase().includes(searchTerm.toLowerCase()) ||
    course.description.toLowerCase().includes(searchTerm.toLowerCase())
  );

  if (loading) {
    return (
      <div className="p-6 space-y-6">
        <div className="animate-pulse space-y-6">
          <div className="h-12 bg-gray-200 dark:bg-gray-700 rounded w-1/3"></div>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {[...Array(3)].map((_, i) => (
              <div key={i} className="h-96 bg-gray-200 dark:bg-gray-700 rounded-xl"></div>
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
          <h1 className="text-3xl font-bold text-gray-900 dark:text-white">My Courses</h1>
          <p className="text-gray-600 dark:text-gray-400 mt-1">
            Manage your courses and video sessions
          </p>
        </div>
        <div className="w-full md:w-96">
          <Input
            placeholder="Search courses..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="w-full"
          />
        </div>
      </div>

      {/* Courses Grid */}
      {filteredCourses.length === 0 ? (
        <div className="text-center py-12">
          <div className="text-6xl mb-4">📚</div>
          <h3 className="text-xl font-semibold text-gray-900 dark:text-white mb-2">
            {searchTerm ? 'No courses found' : 'No courses yet'}
          </h3>
          <p className="text-gray-600 dark:text-gray-400">
            {searchTerm ? 'Try a different search term' : 'Start by creating your first course'}
          </p>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {filteredCourses.map((course) => (
            <CourseCard 
              key={course.id} 
              course={course} 
              onEdit={setEditingCourse}
            />
          ))}
        </div>
      )}

      {/* Edit Course Modal */}
      <AnimatePresence>
        {editingCourse && (
          <EditCourseModal
            course={editingCourse}
            onClose={() => setEditingCourse(null)}
            onSave={loadCourses}
          />
        )}
      </AnimatePresence>
    </div>
  );
};

export default MentorCoursesPage;