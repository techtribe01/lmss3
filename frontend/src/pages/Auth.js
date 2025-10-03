import React, { useState } from "react";
import { useNavigate } from "react-router-dom";
import SignupForm from "../components/auth/SignupForm";
import LoginForm from "../components/auth/LoginForm";
import { useAuth } from "../contexts/AuthContext";

const Auth = () => {
  const [isSignup, setIsSignup] = useState(false);
  const navigate = useNavigate();
  const { login } = useAuth();

  const handleAuthSuccess = async (authData) => {
    // Get the access token from Supabase
    const accessToken = authData.session?.access_token;
    const user = authData.user;
    
    if (accessToken && user) {
      // Extract user metadata
      const userData = {
        id: user.id,
        email: user.email,
        full_name: user.user_metadata?.full_name || user.email,
        username: user.user_metadata?.username || user.email,
        role: user.user_metadata?.role || 'student'
      };
      
      // Login user with Supabase token
      login(accessToken, userData);
      
      // Navigate based on role
      if (userData.role === 'admin') navigate('/admin');
      else if (userData.role === 'mentor') navigate('/mentor');
      else if (userData.role === 'student') navigate('/student');
      else navigate('/'); // fallback
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-blue-50 via-white to-purple-50 p-4">
      <div className="w-full max-w-md">
        <div className="bg-white rounded-2xl shadow-2xl border border-gray-200 overflow-hidden">
          <div className="bg-gradient-to-r from-blue-600 to-purple-600 p-8 text-center">
            <h1 className="text-3xl font-bold text-white mb-2">
              {isSignup ? "Create Account" : "Welcome Back"}
            </h1>
            <p className="text-blue-100">
              {isSignup ? "Join us today" : "Sign in to continue"}
            </p>
          </div>

          <div className="p-8">
            {isSignup ? (
              <SignupForm onSuccess={handleAuthSuccess} />
            ) : (
              <LoginForm onSuccess={handleAuthSuccess} />
            )}

            <div className="mt-6 text-center">
              <button
                onClick={() => setIsSignup(!isSignup)}
                className="text-sm text-gray-600 hover:text-blue-600 transition-colors"
              >
                {isSignup ? (
                  <>
                    Already have an account?{" "}
                    <span className="font-semibold text-blue-600">Sign in</span>
                  </>
                ) : (
                  <>
                    Don't have an account?{" "}
                    <span className="font-semibold text-blue-600">Sign up</span>
                  </>
                )}
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Auth;