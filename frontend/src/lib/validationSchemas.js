import { z } from 'zod';

// Password strength validation
const passwordSchema = z
  .string()
  .min(8, 'Password must be at least 8 characters long')
  .regex(/[A-Z]/, 'Password must contain at least one uppercase letter')
  .regex(/[a-z]/, 'Password must contain at least one lowercase letter')
  .regex(/[0-9]/, 'Password must contain at least one number')
  .regex(/[^A-Za-z0-9]/, 'Password must contain at least one special character');

// Email validation with custom message
const emailSchema = z
  .string()
  .min(1, 'Email is required')
  .email('Please enter a valid email address');

// Username validation
const usernameSchema = z
  .string()
  .min(3, 'Username must be at least 3 characters long')
  .max(20, 'Username must be less than 20 characters')
  .regex(/^[a-zA-Z0-9_]+$/, 'Username can only contain letters, numbers, and underscores');

// Supabase Login form schema (email only)
export const supabaseLoginSchema = z.object({
  email: emailSchema,
  password: z.string().min(1, 'Password is required'),
});

// Original Login form schema (username or email)
export const loginSchema = z.object({
  username: z.string().min(1, 'Username or email is required'),
  password: z.string().min(1, 'Password is required'),
});

// Supabase Registration form schema  
export const supabaseRegisterSchema = z
  .object({
    fullName: z
      .string()
      .trim()
      .min(1, 'Full name is required')
      .max(100, 'Full name must be less than 100 characters'),
    username: z
      .string()
      .trim()
      .min(3, 'Username must be at least 3 characters')
      .max(20, 'Username must be less than 20 characters')
      .regex(/^[a-zA-Z0-9_]+$/, 'Username can only contain letters, numbers, and underscores'),
    email: z
      .string()
      .trim()
      .email('Invalid email address')
      .max(255, 'Email must be less than 255 characters'),
    password: z
      .string()
      .min(8, 'Password must be at least 8 characters')
      .max(128, 'Password must be less than 128 characters'),
    confirmPassword: z.string(),
    role: z.enum(['student', 'mentor', 'admin'], {
      required_error: 'Please select a role',
    }),
  })
  .refine((data) => data.password === data.confirmPassword, {
    message: 'Passwords do not match',
    path: ['confirmPassword'],
  });

// Registration form schema
export const registerSchema = z
  .object({
    full_name: z
      .string()
      .min(2, 'Full name must be at least 2 characters long')
      .max(50, 'Full name must be less than 50 characters'),
    username: usernameSchema,
    email: emailSchema,
    password: passwordSchema,
    confirmPassword: z.string(),
    role: z.enum(['student', 'mentor', 'admin'], {
      required_error: 'Please select a role',
    }),
  })
  .refine((data) => data.password === data.confirmPassword, {
    message: "Passwords don't match",
    path: ['confirmPassword'],
  });

// Course form schema
export const courseSchema = z.object({
  title: z
    .string()
    .min(3, 'Course title must be at least 3 characters long')
    .max(100, 'Course title must be less than 100 characters'),
  description: z
    .string()
    .min(10, 'Description must be at least 10 characters long')
    .max(500, 'Description must be less than 500 characters'),
  instructor: z
    .string()
    .min(2, 'Instructor name is required'),
  duration: z
    .string()
    .min(1, 'Duration is required'),
  level: z.enum(['Beginner', 'Intermediate', 'Advanced'], {
    required_error: 'Please select a level',
  }),
  category: z
    .string()
    .min(2, 'Category is required'),
  price: z
    .number()
    .min(0, 'Price must be a positive number')
    .optional(),
});

// User profile schema
export const userProfileSchema = z.object({
  full_name: z
    .string()
    .min(2, 'Full name must be at least 2 characters long')
    .max(50, 'Full name must be less than 50 characters'),
  email: emailSchema,
  department: z
    .string()
    .min(2, 'Department is required')
    .optional(),
  bio: z
    .string()
    .max(200, 'Bio must be less than 200 characters')
    .optional(),
});

// Assignment submission schema
export const assignmentSubmissionSchema = z.object({
  title: z
    .string()
    .min(3, 'Assignment title must be at least 3 characters long')
    .max(100, 'Assignment title must be less than 100 characters'),
  description: z
    .string()
    .min(10, 'Description must be at least 10 characters long')
    .max(1000, 'Description must be less than 1000 characters'),
  dueDate: z
    .date({
      required_error: 'Due date is required',
    })
    .min(new Date(), 'Due date must be in the future'),
});

// Grade schema
export const gradeSchema = z.object({
  score: z
    .number()
    .min(0, 'Score must be at least 0')
    .max(100, 'Score must be at most 100'),
  feedback: z
    .string()
    .min(5, 'Feedback must be at least 5 characters long')
    .max(500, 'Feedback must be less than 500 characters'),
});

// Search and filter schemas
export const searchSchema = z.object({
  query: z.string().optional(),
  category: z.string().optional(),
  level: z.string().optional(),
  instructor: z.string().optional(),
});