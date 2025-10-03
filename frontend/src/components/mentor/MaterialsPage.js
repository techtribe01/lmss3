import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { useAuth } from '../../contexts/AuthContext';
import { useToast } from '../../hooks/use-toast';
import * as mockService from '../../services/mockService';
import { Button } from '../ui/button';
import { Input } from '../ui/input';
import { Label } from '../ui/label';

const MaterialCard = ({ material, onDelete }) => {
  const getFileIcon = (type) => {
    if (type?.includes('pdf')) return '📄';
    if (type?.includes('video')) return '🎥';
    if (type?.includes('image')) return '🖼️';
    if (type?.includes('zip') || type?.includes('archive')) return '📦';
    return '📎';
  };

  const formatFileSize = (bytes) => {
    if (!bytes) return 'N/A';
    if (bytes < 1024) return bytes + ' B';
    if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(2) + ' KB';
    return (bytes / (1024 * 1024)).toFixed(2) + ' MB';
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className="bg-white dark:bg-gray-800 rounded-lg shadow-lg p-6 hover:shadow-xl transition-shadow"
    >
      <div className="flex items-start gap-4">
        <div className="text-5xl">{getFileIcon(material.file_type)}</div>
        <div className="flex-1 min-w-0">
          <h3 className="text-lg font-bold text-gray-900 dark:text-white truncate">
            {material.title}
          </h3>
          <p className="text-sm text-gray-600 dark:text-gray-400 mt-1">
            {material.course_name}
          </p>
          {material.description && (
            <p className="text-sm text-gray-600 dark:text-gray-400 mt-2 line-clamp-2">
              {material.description}
            </p>
          )}
          <div className="flex items-center gap-4 mt-3 text-xs text-gray-500 dark:text-gray-400">
            <span>📦 {formatFileSize(material.file_size)}</span>
            <span>📅 {new Date(material.uploaded_at).toLocaleDateString()}</span>
            <span>⬇️ {material.downloads || 0} downloads</span>
          </div>
        </div>
      </div>
      
      <div className="flex gap-2 mt-4">
        <Button variant="outline" className="flex-1" size="sm">
          👁️ View
        </Button>
        <Button variant="outline" className="flex-1" size="sm">
          ⬇️ Download
        </Button>
        <Button 
          variant="outline" 
          className="text-red-600 hover:text-red-700 hover:bg-red-50 dark:hover:bg-red-900/20"
          size="sm"
          onClick={() => onDelete(material.id)}
        >
          🗑️ Delete
        </Button>
      </div>
    </motion.div>
  );
};

const UploadMaterialModal = ({ onClose, onSave, courses }) => {
  const { toast } = useToast();
  const [formData, setFormData] = useState({
    title: '',
    description: '',
    course_id: '',
    file: null
  });
  const [uploading, setUploading] = useState(false);

  const handleFileChange = (e) => {
    const file = e.target.files[0];
    if (file) {
      setFormData({ ...formData, file });
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setUploading(true);
    
    try {
      // Simulate file upload
      await new Promise(resolve => setTimeout(resolve, 1500));
      
      const material = {
        title: formData.title,
        description: formData.description,
        course_id: formData.course_id,
        file_name: formData.file?.name || 'document.pdf',
        file_type: formData.file?.type || 'application/pdf',
        file_size: formData.file?.size || 1024000,
        uploaded_at: new Date().toISOString(),
        downloads: 0
      };
      
      // In real implementation, this would upload to server
      toast({
        title: 'Success',
        description: 'Material uploaded successfully!'
      });
      onSave();
      onClose();
    } catch (error) {
      toast({
        title: 'Error',
        description: 'Failed to upload material',
        variant: 'destructive'
      });
    } finally {
      setUploading(false);
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
        className="bg-white dark:bg-gray-800 rounded-xl shadow-2xl max-w-2xl w-full"
        onClick={(e) => e.stopPropagation()}
      >
        <div className="p-6 border-b border-gray-200 dark:border-gray-700">
          <h2 className="text-2xl font-bold text-gray-900 dark:text-white">Upload Material</h2>
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

          <div className="space-y-2">
            <Label htmlFor="title">Material Title *</Label>
            <Input
              id="title"
              value={formData.title}
              onChange={(e) => setFormData({ ...formData, title: e.target.value })}
              placeholder="e.g., Week 1 Lecture Notes"
              required
            />
          </div>

          <div className="space-y-2">
            <Label htmlFor="description">Description</Label>
            <Input
              id="description"
              value={formData.description}
              onChange={(e) => setFormData({ ...formData, description: e.target.value })}
              placeholder="Brief description of the material"
            />
          </div>

          <div className="space-y-2">
            <Label htmlFor="file">Upload File *</Label>
            <input
              id="file"
              type="file"
              onChange={handleFileChange}
              className="flex h-10 w-full rounded-md border border-input bg-white dark:bg-gray-800 px-3 py-2 text-sm text-gray-900 dark:text-gray-100 file:border-0 file:bg-transparent file:text-sm file:font-medium focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-blue-500"
              required
            />
            {formData.file && (
              <p className="text-xs text-gray-600 dark:text-gray-400">
                Selected: {formData.file.name} ({(formData.file.size / 1024).toFixed(2)} KB)
              </p>
            )}
          </div>

          <div className="flex gap-3 pt-4">
            <Button
              type="button"
              onClick={onClose}
              variant="outline"
              className="flex-1"
              disabled={uploading}
            >
              Cancel
            </Button>
            <Button
              type="submit"
              className="flex-1 bg-gradient-to-r from-blue-600 to-purple-600 hover:opacity-90"
              disabled={uploading}
            >
              {uploading ? '⏳ Uploading...' : '📤 Upload Material'}
            </Button>
          </div>
        </form>
      </motion.div>
    </motion.div>
  );
};

const MaterialsPage = () => {
  const { user } = useAuth();
  const { toast } = useToast();
  const [materials, setMaterials] = useState([]);
  const [courses, setCourses] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showUploadModal, setShowUploadModal] = useState(false);
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
      
      // Mock materials data
      const mockMaterials = coursesData.flatMap(course => [
        {
          id: `mat-${course.id}-1`,
          title: `${course.title} - Lecture Slides`,
          description: 'Complete lecture slides for the course',
          course_id: course.id,
          course_name: course.title,
          file_name: 'lecture-slides.pdf',
          file_type: 'application/pdf',
          file_size: 2048000,
          uploaded_at: new Date(Date.now() - 86400000 * 5).toISOString(),
          downloads: 45
        },
        {
          id: `mat-${course.id}-2`,
          title: `${course.title} - Code Examples`,
          description: 'Sample code and examples',
          course_id: course.id,
          course_name: course.title,
          file_name: 'code-examples.zip',
          file_type: 'application/zip',
          file_size: 5120000,
          uploaded_at: new Date(Date.now() - 86400000 * 3).toISOString(),
          downloads: 32
        }
      ]);
      
      setMaterials(mockMaterials);
    } catch (error) {
      console.error('Error loading data:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleDelete = async (materialId) => {
    if (window.confirm('Are you sure you want to delete this material?')) {
      setMaterials(materials.filter(m => m.id !== materialId));
      toast({
        title: 'Success',
        description: 'Material deleted successfully'
      });
    }
  };

  const filteredMaterials = filterCourse === 'all' 
    ? materials 
    : materials.filter(m => m.course_id === filterCourse);

  if (loading) {
    return (
      <div className="p-6">
        <div className="animate-pulse space-y-6">
          <div className="h-12 bg-gray-200 dark:bg-gray-700 rounded w-1/3"></div>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {[...Array(4)].map((_, i) => (
              <div key={i} className="h-48 bg-gray-200 dark:bg-gray-700 rounded-lg"></div>
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
          <h1 className="text-3xl font-bold text-gray-900 dark:text-white">Course Materials</h1>
          <p className="text-gray-600 dark:text-gray-400 mt-1">
            Upload and manage course materials
          </p>
        </div>
        <Button 
          onClick={() => setShowUploadModal(true)}
          className="bg-gradient-to-r from-blue-600 to-purple-600 hover:opacity-90"
        >
          📤 Upload Material
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

      {/* Materials Grid */}
      {filteredMaterials.length === 0 ? (
        <div className="text-center py-12">
          <div className="text-6xl mb-4">📁</div>
          <h3 className="text-xl font-semibold text-gray-900 dark:text-white mb-2">
            No materials yet
          </h3>
          <p className="text-gray-600 dark:text-gray-400 mb-4">
            Upload your first course material to get started
          </p>
          <Button 
            onClick={() => setShowUploadModal(true)}
            className="bg-gradient-to-r from-blue-600 to-purple-600 hover:opacity-90"
          >
            Upload Material
          </Button>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {filteredMaterials.map((material) => (
            <MaterialCard 
              key={material.id} 
              material={material}
              onDelete={handleDelete}
            />
          ))}
        </div>
      )}

      {/* Upload Modal */}
      <AnimatePresence>
        {showUploadModal && (
          <UploadMaterialModal
            onClose={() => setShowUploadModal(false)}
            onSave={loadData}
            courses={courses}
          />
        )}
      </AnimatePresence>
    </div>
  );
};

export default MaterialsPage;