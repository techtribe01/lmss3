import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { useAuth } from '../../contexts/AuthContext';
import { useToast } from '../../hooks/use-toast';
import * as mockService from '../../services/mockService';
import { Button } from '../ui/button';
import { Input } from '../ui/input';
import { Label } from '../ui/label';
import { Textarea } from '../ui/textarea';

const TaskCard = ({ task, onView }) => (
  <motion.div
    initial={{ opacity: 0, y: 20 }}
    animate={{ opacity: 1, y: 0 }}
    className="bg-white dark:bg-gray-800 rounded-lg shadow-lg p-6 hover:shadow-xl transition-shadow"
  >
    <div className="flex items-start justify-between mb-4">
      <div>
        <h3 className="text-lg font-bold text-gray-900 dark:text-white">{task.title}</h3>
        <p className="text-sm text-gray-600 dark:text-gray-400 mt-1">{task.course_name}</p>
      </div>
      <span className={`px-3 py-1 rounded-full text-xs font-medium ${
        task.status === 'active' ? 'bg-green-100 text-green-800 dark:bg-green-900/30 dark:text-green-400' :
        'bg-gray-100 text-gray-800 dark:bg-gray-700 dark:text-gray-400'
      }`}>
        {task.status}
      </span>
    </div>
    
    <p className="text-gray-600 dark:text-gray-400 text-sm mb-4 line-clamp-2">
      {task.description}
    </p>
    
    <div className="grid grid-cols-3 gap-4 mb-4 text-center">
      <div>
        <p className="text-xl font-bold text-blue-600 dark:text-blue-400">{task.total_submissions || 0}</p>
        <p className="text-xs text-gray-600 dark:text-gray-400">Submissions</p>
      </div>
      <div>
        <p className="text-xl font-bold text-yellow-600 dark:text-yellow-400">{task.pending_review || 0}</p>
        <p className="text-xs text-gray-600 dark:text-gray-400">Pending</p>
      </div>
      <div>
        <p className="text-xl font-bold text-green-600 dark:text-green-400">{task.graded || 0}</p>
        <p className="text-xs text-gray-600 dark:text-gray-400">Graded</p>
      </div>
    </div>
    
    <div className="flex items-center justify-between text-sm text-gray-600 dark:text-gray-400 mb-4">
      <span>📅 Due: {new Date(task.due_date).toLocaleDateString()}</span>
      <span>⭐ {task.max_score} points</span>
    </div>
    
    <Button onClick={() => onView(task)} className="w-full">
      View Submissions
    </Button>
  </motion.div>
);

const CreateTaskModal = ({ onClose, onSave, courses }) => {
  const { toast } = useToast();
  const [formData, setFormData] = useState({
    title: '',
    description: '',
    course_id: '',
    due_date: '',
    max_score: 100
  });
  const [saving, setSaving] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setSaving(true);
    
    try {
      await mockService.createTask({
        ...formData,
        status: 'active',
        total_submissions: 0,
        pending_review: 0,
        graded: 0
      });
      toast({
        title: 'Success',
        description: 'Task created successfully!'
      });
      onSave();
      onClose();
    } catch (error) {
      toast({
        title: 'Error',
        description: 'Failed to create task',
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
        <div className="sticky top-0 bg-white dark:bg-gray-800 border-b border-gray-200 dark:border-gray-700 p-6">
          <h2 className="text-2xl font-bold text-gray-900 dark:text-white">Create New Task</h2>
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
            <Label htmlFor="title">Task Title *</Label>
            <Input
              id="title"
              value={formData.title}
              onChange={(e) => setFormData({ ...formData, title: e.target.value })}
              placeholder="e.g., React Hooks Assignment"
              required
            />
          </div>

          <div className="space-y-2">
            <Label htmlFor="description">Description *</Label>
            <Textarea
              id="description"
              value={formData.description}
              onChange={(e) => setFormData({ ...formData, description: e.target.value })}
              placeholder="Describe the task requirements..."
              rows={4}
              required
            />
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div className="space-y-2">
              <Label htmlFor="due_date">Due Date *</Label>
              <Input
                id="due_date"
                type="datetime-local"
                value={formData.due_date}
                onChange={(e) => setFormData({ ...formData, due_date: e.target.value })}
                required
              />
            </div>
            
            <div className="space-y-2">
              <Label htmlFor="max_score">Max Score *</Label>
              <Input
                id="max_score"
                type="number"
                value={formData.max_score}
                onChange={(e) => setFormData({ ...formData, max_score: parseInt(e.target.value) })}
                required
              />
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
              {saving ? 'Creating...' : 'Create Task'}
            </Button>
          </div>
        </form>
      </motion.div>
    </motion.div>
  );
};

const TaskAssignmentPage = () => {
  const { user } = useAuth();
  const [tasks, setTasks] = useState([]);
  const [courses, setCourses] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [filterStatus, setFilterStatus] = useState('all');

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    try {
      setLoading(true);
      const [tasksData, coursesData] = await Promise.all([
        mockService.getTasks({ instructor_id: user?.id }),
        mockService.getCourses({ instructor_id: user?.id })
      ]);
      setTasks(tasksData);
      setCourses(coursesData);
    } catch (error) {
      console.error('Error loading data:', error);
    } finally {
      setLoading(false);
    }
  };

  const filteredTasks = tasks.filter(task => 
    filterStatus === 'all' || task.status === filterStatus
  );

  if (loading) {
    return (
      <div className="p-6 space-y-6">
        <div className="animate-pulse space-y-6">
          <div className="h-12 bg-gray-200 dark:bg-gray-700 rounded w-1/3"></div>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {[...Array(3)].map((_, i) => (
              <div key={i} className="h-64 bg-gray-200 dark:bg-gray-700 rounded-lg"></div>
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
          <h1 className="text-3xl font-bold text-gray-900 dark:text-white">Task Assignment</h1>
          <p className="text-gray-600 dark:text-gray-400 mt-1">
            Create and manage tasks for your students
          </p>
        </div>
        <Button 
          onClick={() => setShowCreateModal(true)}
          className="bg-gradient-to-r from-blue-600 to-purple-600 hover:opacity-90"
        >
          ➕ Create New Task
        </Button>
      </div>

      {/* Filter */}
      <div className="flex gap-2">
        <Button
          variant={filterStatus === 'all' ? 'default' : 'outline'}
          onClick={() => setFilterStatus('all')}
          size="sm"
        >
          All Tasks
        </Button>
        <Button
          variant={filterStatus === 'active' ? 'default' : 'outline'}
          onClick={() => setFilterStatus('active')}
          size="sm"
        >
          Active
        </Button>
        <Button
          variant={filterStatus === 'completed' ? 'default' : 'outline'}
          onClick={() => setFilterStatus('completed')}
          size="sm"
        >
          Completed
        </Button>
      </div>

      {/* Tasks Grid */}
      {filteredTasks.length === 0 ? (
        <div className="text-center py-12">
          <div className="text-6xl mb-4">📝</div>
          <h3 className="text-xl font-semibold text-gray-900 dark:text-white mb-2">
            No tasks yet
          </h3>
          <p className="text-gray-600 dark:text-gray-400 mb-4">
            Create your first task to get started
          </p>
          <Button 
            onClick={() => setShowCreateModal(true)}
            className="bg-gradient-to-r from-blue-600 to-purple-600 hover:opacity-90"
          >
            Create Task
          </Button>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {filteredTasks.map((task) => (
            <TaskCard 
              key={task.id} 
              task={task} 
              onView={(task) => console.log('View task:', task)}
            />
          ))}
        </div>
      )}

      {/* Create Task Modal */}
      <AnimatePresence>
        {showCreateModal && (
          <CreateTaskModal
            onClose={() => setShowCreateModal(false)}
            onSave={loadData}
            courses={courses}
          />
        )}
      </AnimatePresence>
    </div>
  );
};

export default TaskAssignmentPage;