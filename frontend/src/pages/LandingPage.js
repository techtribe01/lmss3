import React from 'react';
import { Link } from 'react-router-dom';
import { motion } from 'framer-motion';
import { 
  BookOpen, Users, Award, Video, Clock, CheckCircle, 
  Star, ArrowRight, Menu, X, ChevronRight, Sparkles,
  BarChart3, Shield, Zap, Globe
} from 'lucide-react';

const LandingPage = () => {
  const [mobileMenuOpen, setMobileMenuOpen] = React.useState(false);

  const features = [
    {
      icon: <BookOpen className="w-6 h-6" />,
      title: "Comprehensive Courses",
      description: "Access a wide range of courses designed by industry experts"
    },
    {
      icon: <Video className="w-6 h-6" />,
      title: "Live Sessions",
      description: "Join interactive video sessions with mentors and peers"
    },
    {
      icon: <Award className="w-6 h-6" />,
      title: "Certifications",
      description: "Earn recognized certificates upon course completion"
    },
    {
      icon: <Users className="w-6 h-6" />,
      title: "Expert Mentors",
      description: "Learn from experienced professionals in the field"
    },
    {
      icon: <Clock className="w-6 h-6" />,
      title: "Flexible Learning",
      description: "Study at your own pace with 24/7 access to materials"
    },
    {
      icon: <BarChart3 className="w-6 h-6" />,
      title: "Track Progress",
      description: "Monitor your learning journey with detailed analytics"
    }
  ];

  const stats = [
    { label: "Active Students", value: "10,000+" },
    { label: "Expert Mentors", value: "500+" },
    { label: "Courses Available", value: "200+" },
    { label: "Success Rate", value: "95%" }
  ];

  const testimonials = [
    {
      name: "Sarah Johnson",
      role: "Software Developer",
      image: "https://images.unsplash.com/photo-1494790108377-be9c29b29330?w=150",
      text: "This LMS transformed my career. The mentors are exceptional and the content is top-notch!"
    },
    {
      name: "Michael Chen",
      role: "Data Scientist",
      image: "https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=150",
      text: "The flexible learning schedule allowed me to upskill while working full-time. Highly recommended!"
    },
    {
      name: "Emily Rodriguez",
      role: "UX Designer",
      image: "https://images.unsplash.com/photo-1438761681033-6461ffad8d80?w=150",
      text: "The certification I earned here helped me land my dream job. The platform is incredibly user-friendly!"
    }
  ];

  return (
    <div className="min-h-screen bg-gradient-to-b from-slate-50 to-white dark:from-slate-900 dark:to-slate-800">
      {/* Navigation */}
      <nav className="fixed top-0 w-full bg-white/80 dark:bg-slate-900/80 backdrop-blur-md z-50 border-b border-slate-200 dark:border-slate-700">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            <div className="flex items-center gap-2">
              <div className="w-10 h-10 bg-gradient-to-br from-blue-500 to-purple-600 rounded-xl flex items-center justify-center">
                <BookOpen className="w-6 h-6 text-white" />
              </div>
              <span className="text-xl font-bold bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">
                EduPlatform
              </span>
            </div>

            {/* Desktop Menu */}
            <div className="hidden md:flex items-center gap-8">
              <a href="#features" className="text-slate-600 dark:text-slate-300 hover:text-blue-600 dark:hover:text-blue-400 transition-colors">
                Features
              </a>
              <a href="#testimonials" className="text-slate-600 dark:text-slate-300 hover:text-blue-600 dark:hover:text-blue-400 transition-colors">
                Testimonials
              </a>
              <a href="#pricing" className="text-slate-600 dark:text-slate-300 hover:text-blue-600 dark:hover:text-blue-400 transition-colors">
                Pricing
              </a>
              <Link 
                to="/auth" 
                className="px-6 py-2 bg-gradient-to-r from-blue-600 to-purple-600 text-white rounded-lg hover:shadow-lg hover:scale-105 transition-all duration-200"
              >
                Get Started
              </Link>
            </div>

            {/* Mobile Menu Button */}
            <button 
              className="md:hidden"
              onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
            >
              {mobileMenuOpen ? <X /> : <Menu />}
            </button>
          </div>
        </div>

        {/* Mobile Menu */}
        {mobileMenuOpen && (
          <motion.div 
            initial={{ opacity: 0, y: -20 }}
            animate={{ opacity: 1, y: 0 }}
            className="md:hidden bg-white dark:bg-slate-900 border-t border-slate-200 dark:border-slate-700"
          >
            <div className="px-4 py-4 space-y-3">
              <a href="#features" className="block text-slate-600 dark:text-slate-300 hover:text-blue-600 py-2">
                Features
              </a>
              <a href="#testimonials" className="block text-slate-600 dark:text-slate-300 hover:text-blue-600 py-2">
                Testimonials
              </a>
              <a href="#pricing" className="block text-slate-600 dark:text-slate-300 hover:text-blue-600 py-2">
                Pricing
              </a>
              <Link 
                to="/auth" 
                className="block text-center px-6 py-2 bg-gradient-to-r from-blue-600 to-purple-600 text-white rounded-lg"
              >
                Get Started
              </Link>
            </div>
          </motion.div>
        )}
      </nav>

      {/* Hero Section */}
      <section className="pt-32 pb-20 px-4 sm:px-6 lg:px-8">
        <div className="max-w-7xl mx-auto">
          <div className="grid lg:grid-cols-2 gap-12 items-center">
            <motion.div
              initial={{ opacity: 0, x: -50 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ duration: 0.6 }}
            >
              <div className="inline-flex items-center gap-2 px-4 py-2 bg-blue-50 dark:bg-blue-900/30 rounded-full text-blue-600 dark:text-blue-400 text-sm font-medium mb-6">
                <Sparkles className="w-4 h-4" />
                <span>Transform Your Learning Journey</span>
              </div>
              
              <h1 className="text-5xl sm:text-6xl font-bold text-slate-900 dark:text-white mb-6 leading-tight">
                Learn, Grow, and
                <span className="bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent"> Excel</span>
              </h1>
              
              <p className="text-xl text-slate-600 dark:text-slate-300 mb-8 leading-relaxed">
                Join thousands of students in mastering new skills with our comprehensive learning management system. Expert mentors, flexible schedules, and industry-recognized certifications.
              </p>

              <div className="flex flex-col sm:flex-row gap-4 mb-8">
                <Link 
                  to="/auth" 
                  className="inline-flex items-center justify-center gap-2 px-8 py-4 bg-gradient-to-r from-blue-600 to-purple-600 text-white rounded-xl hover:shadow-xl hover:scale-105 transition-all duration-200 font-semibold"
                >
                  Start Learning Free
                  <ArrowRight className="w-5 h-5" />
                </Link>
                <a 
                  href="#features"
                  className="inline-flex items-center justify-center gap-2 px-8 py-4 bg-white dark:bg-slate-800 text-slate-900 dark:text-white rounded-xl border-2 border-slate-200 dark:border-slate-700 hover:border-blue-600 dark:hover:border-blue-400 transition-all duration-200 font-semibold"
                >
                  Learn More
                  <ChevronRight className="w-5 h-5" />
                </a>
              </div>

              <div className="flex items-center gap-6">
                <div className="flex -space-x-2">
                  {[1, 2, 3, 4].map((i) => (
                    <img
                      key={i}
                      src={`https://i.pravatar.cc/150?img=${i}`}
                      alt="Student"
                      className="w-10 h-10 rounded-full border-2 border-white dark:border-slate-900"
                    />
                  ))}
                </div>
                <div>
                  <div className="flex items-center gap-1">
                    {[1, 2, 3, 4, 5].map((i) => (
                      <Star key={i} className="w-4 h-4 fill-yellow-400 text-yellow-400" />
                    ))}
                  </div>
                  <p className="text-sm text-slate-600 dark:text-slate-400">
                    <span className="font-semibold">4.9/5</span> from 10,000+ students
                  </p>
                </div>
              </div>
            </motion.div>

            <motion.div
              initial={{ opacity: 0, x: 50 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ duration: 0.6, delay: 0.2 }}
              className="relative"
            >
              <div className="relative z-10 rounded-2xl overflow-hidden shadow-2xl">
                <img
                  src="https://images.unsplash.com/photo-1522202176988-66273c2fd55f?w=800"
                  alt="Students learning"
                  className="w-full h-auto"
                />
              </div>
              
              {/* Floating Cards */}
              <motion.div
                animate={{ y: [0, -10, 0] }}
                transition={{ duration: 3, repeat: Infinity }}
                className="absolute -top-4 -right-4 bg-white dark:bg-slate-800 rounded-xl shadow-xl p-4 z-20"
              >
                <div className="flex items-center gap-3">
                  <div className="w-12 h-12 bg-green-100 dark:bg-green-900/30 rounded-lg flex items-center justify-center">
                    <CheckCircle className="w-6 h-6 text-green-600 dark:text-green-400" />
                  </div>
                  <div>
                    <p className="text-sm font-semibold text-slate-900 dark:text-white">Course Completed</p>
                    <p className="text-xs text-slate-500 dark:text-slate-400">Web Development</p>
                  </div>
                </div>
              </motion.div>

              <motion.div
                animate={{ y: [0, 10, 0] }}
                transition={{ duration: 3, repeat: Infinity, delay: 1 }}
                className="absolute -bottom-4 -left-4 bg-white dark:bg-slate-800 rounded-xl shadow-xl p-4 z-20"
              >
                <div className="flex items-center gap-3">
                  <div className="w-12 h-12 bg-purple-100 dark:bg-purple-900/30 rounded-lg flex items-center justify-center">
                    <Award className="w-6 h-6 text-purple-600 dark:text-purple-400" />
                  </div>
                  <div>
                    <p className="text-sm font-semibold text-slate-900 dark:text-white">Certificate Earned</p>
                    <p className="text-xs text-slate-500 dark:text-slate-400">95% Score</p>
                  </div>
                </div>
              </motion.div>
            </motion.div>
          </div>
        </div>
      </section>

      {/* Stats Section */}
      <section className="py-12 bg-white dark:bg-slate-800/50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="grid grid-cols-2 md:grid-cols-4 gap-8">
            {stats.map((stat, index) => (
              <motion.div
                key={index}
                initial={{ opacity: 0, y: 20 }}
                whileInView={{ opacity: 1, y: 0 }}
                transition={{ delay: index * 0.1 }}
                className="text-center"
              >
                <p className="text-4xl font-bold bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent mb-2">
                  {stat.value}
                </p>
                <p className="text-slate-600 dark:text-slate-400">{stat.label}</p>
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section id="features" className="py-20 px-4 sm:px-6 lg:px-8">
        <div className="max-w-7xl mx-auto">
          <div className="text-center mb-16">
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
            >
              <h2 className="text-4xl font-bold text-slate-900 dark:text-white mb-4">
                Everything You Need to Succeed
              </h2>
              <p className="text-xl text-slate-600 dark:text-slate-300">
                Powerful features to enhance your learning experience
              </p>
            </motion.div>
          </div>

          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-8">
            {features.map((feature, index) => (
              <motion.div
                key={index}
                initial={{ opacity: 0, y: 20 }}
                whileInView={{ opacity: 1, y: 0 }}
                transition={{ delay: index * 0.1 }}
                className="bg-white dark:bg-slate-800 rounded-2xl p-6 shadow-lg hover:shadow-xl transition-all duration-300 hover:-translate-y-1"
              >
                <div className="w-12 h-12 bg-gradient-to-br from-blue-500 to-purple-600 rounded-xl flex items-center justify-center text-white mb-4">
                  {feature.icon}
                </div>
                <h3 className="text-xl font-semibold text-slate-900 dark:text-white mb-2">
                  {feature.title}
                </h3>
                <p className="text-slate-600 dark:text-slate-400">
                  {feature.description}
                </p>
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      {/* Testimonials Section */}
      <section id="testimonials" className="py-20 bg-slate-50 dark:bg-slate-900/50 px-4 sm:px-6 lg:px-8">
        <div className="max-w-7xl mx-auto">
          <div className="text-center mb-16">
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
            >
              <h2 className="text-4xl font-bold text-slate-900 dark:text-white mb-4">
                What Our Students Say
              </h2>
              <p className="text-xl text-slate-600 dark:text-slate-300">
                Join thousands of satisfied learners
              </p>
            </motion.div>
          </div>

          <div className="grid md:grid-cols-3 gap-8">
            {testimonials.map((testimonial, index) => (
              <motion.div
                key={index}
                initial={{ opacity: 0, y: 20 }}
                whileInView={{ opacity: 1, y: 0 }}
                transition={{ delay: index * 0.1 }}
                className="bg-white dark:bg-slate-800 rounded-2xl p-6 shadow-lg"
              >
                <div className="flex items-center gap-1 mb-4">
                  {[1, 2, 3, 4, 5].map((i) => (
                    <Star key={i} className="w-4 h-4 fill-yellow-400 text-yellow-400" />
                  ))}
                </div>
                <p className="text-slate-600 dark:text-slate-300 mb-6">
                  "{testimonial.text}"
                </p>
                <div className="flex items-center gap-3">
                  <img
                    src={testimonial.image}
                    alt={testimonial.name}
                    className="w-12 h-12 rounded-full"
                  />
                  <div>
                    <p className="font-semibold text-slate-900 dark:text-white">
                      {testimonial.name}
                    </p>
                    <p className="text-sm text-slate-500 dark:text-slate-400">
                      {testimonial.role}
                    </p>
                  </div>
                </div>
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-20 px-4 sm:px-6 lg:px-8">
        <div className="max-w-4xl mx-auto">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            className="bg-gradient-to-r from-blue-600 to-purple-600 rounded-3xl p-12 text-center text-white shadow-2xl"
          >
            <h2 className="text-4xl font-bold mb-4">
              Ready to Start Your Learning Journey?
            </h2>
            <p className="text-xl mb-8 text-blue-50">
              Join thousands of students achieving their goals every day
            </p>
            <Link 
              to="/auth"
              className="inline-flex items-center gap-2 px-8 py-4 bg-white text-blue-600 rounded-xl hover:shadow-xl hover:scale-105 transition-all duration-200 font-semibold"
            >
              Get Started for Free
              <ArrowRight className="w-5 h-5" />
            </Link>
          </motion.div>
        </div>
      </section>

      {/* Footer */}
      <footer className="bg-slate-900 text-white py-12 px-4 sm:px-6 lg:px-8">
        <div className="max-w-7xl mx-auto">
          <div className="grid md:grid-cols-4 gap-8 mb-8">
            <div>
              <div className="flex items-center gap-2 mb-4">
                <div className="w-8 h-8 bg-gradient-to-br from-blue-500 to-purple-600 rounded-lg flex items-center justify-center">
                  <BookOpen className="w-5 h-5" />
                </div>
                <span className="text-lg font-bold">EduPlatform</span>
              </div>
              <p className="text-slate-400">
                Empowering learners worldwide with quality education
              </p>
            </div>
            
            <div>
              <h4 className="font-semibold mb-4">Product</h4>
              <ul className="space-y-2 text-slate-400">
                <li><a href="#" className="hover:text-white">Features</a></li>
                <li><a href="#" className="hover:text-white">Pricing</a></li>
                <li><a href="#" className="hover:text-white">Testimonials</a></li>
              </ul>
            </div>

            <div>
              <h4 className="font-semibold mb-4">Company</h4>
              <ul className="space-y-2 text-slate-400">
                <li><a href="#" className="hover:text-white">About</a></li>
                <li><a href="#" className="hover:text-white">Blog</a></li>
                <li><a href="#" className="hover:text-white">Careers</a></li>
              </ul>
            </div>

            <div>
              <h4 className="font-semibold mb-4">Legal</h4>
              <ul className="space-y-2 text-slate-400">
                <li><a href="#" className="hover:text-white">Privacy</a></li>
                <li><a href="#" className="hover:text-white">Terms</a></li>
                <li><a href="#" className="hover:text-white">Security</a></li>
              </ul>
            </div>
          </div>

          <div className="border-t border-slate-800 pt-8 text-center text-slate-400">
            <p>&copy; 2025 EduPlatform. All rights reserved.</p>
          </div>
        </div>
      </footer>
    </div>
  );
};

export default LandingPage;
