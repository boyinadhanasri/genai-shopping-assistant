import React, { useState, useEffect } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { 
  Sparkles, 
  User, 
  Mail, 
  Lock, 
  Eye, 
  EyeOff, 
  ArrowRight, 
  ArrowLeft,
  AlertCircle,
  ShieldCheck,
  Edit2
} from 'lucide-react';
import PasswordStrengthMeter from '../components/PasswordStrengthMeter';
import api from '../services/api';

export default function Register() {
  const navigate = useNavigate();

  // 2-Step Flow: 'email_input' | 'email_exists' | 'account_details'
  const [step, setStep] = useState('email_input');
  
  const [email, setEmail] = useState('');
  const [name, setName] = useState('');
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  
  const [showPassword, setShowPassword] = useState(false);
  const [showConfirmPassword, setShowConfirmPassword] = useState(false);
  
  const [checkingEmail, setCheckingEmail] = useState(false);
  const [registering, setRegistering] = useState(false);
  const [error, setError] = useState('');

  // Auto-login check
  useEffect(() => {
    const token = localStorage.getItem('shopai_token');
    const user = api.getCurrentUser();
    if (token && user && user.id) {
      navigate('/dashboard', { replace: true });
    }
  }, [navigate]);

  // Real-time password criteria evaluation
  const isPasswordValid = 
    password.length >= 8 &&
    /[A-Z]/.test(password) &&
    /[a-z]/.test(password) &&
    /[0-9]/.test(password) &&
    /[!@#$%^&*(),.?":{}|<>\-_+=[\]\\/`~;']/.test(password);

  // Step 1: Check Email
  const handleCheckEmail = async (e) => {
    e.preventDefault();
    setError('');

    const cleanEmail = email.trim().toLowerCase();
    if (!cleanEmail) {
      setError('Please enter your email address.');
      return;
    }

    setCheckingEmail(true);
    try {
      const res = await api.checkEmail(cleanEmail);
      if (res.exists) {
        // CASE A: Email already registered
        setStep('email_exists');
      } else {
        // CASE B: New email -> Reveal full registration fields
        setStep('account_details');
      }
    } catch (err) {
      setError(err.message || 'Failed to check email. Please try again.');
    } finally {
      setCheckingEmail(false);
    }
  };

  // Step 2: Submit Registration
  const handleRegister = async (e) => {
    e.preventDefault();
    setError('');

    if (!name.trim()) {
      setError('Full Name is required.');
      return;
    }
    if (!password) {
      setError('Password cannot be empty.');
      return;
    }
    if (!confirmPassword) {
      setError('Please confirm your password.');
      return;
    }
    if (password !== confirmPassword) {
      setError('Passwords do not match.');
      return;
    }
    if (!isPasswordValid) {
      setError('Password must meet all complexity requirements.');
      return;
    }

    setRegistering(true);
    try {
      await api.register({
        name: name.trim(),
        email: email.trim().toLowerCase(),
        password,
        confirm_password: confirmPassword,
      });

      // Navigate to OTP verification screen
      navigate(`/verify-otp?email=${encodeURIComponent(email.trim().toLowerCase())}`);
    } catch (err) {
      setError(err.message || 'Registration failed. Please try again.');
    } finally {
      setRegistering(false);
    }
  };

  return (
    <div className="min-h-screen relative flex items-center justify-center p-4 bg-slate-900 overflow-hidden font-sans">
      {/* Dynamic Background Glows */}
      <div className="absolute top-1/4 -left-32 w-96 h-96 bg-indigo-600/30 rounded-full blur-[128px] pointer-events-none" />
      <div className="absolute bottom-1/4 -right-32 w-96 h-96 bg-purple-600/30 rounded-full blur-[128px] pointer-events-none" />
      <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[600px] h-[600px] bg-pink-500/10 rounded-full blur-[150px] pointer-events-none" />

      <div className="relative z-10 w-full max-w-md my-8">
        
        {/* Brand Header */}
        <div className="text-center mb-6">
          <Link to="/" className="inline-flex items-center justify-center w-14 h-14 rounded-2xl ai-gradient-bg text-white shadow-xl shadow-indigo-500/30 mb-3 transform hover:scale-105 transition-transform">
            <Sparkles className="w-8 h-8 animate-pulse" />
          </Link>
          <h1 className="text-2xl sm:text-3xl font-extrabold text-white tracking-tight">
            Create Account
          </h1>
          <p className="text-slate-400 text-xs sm:text-sm mt-1">
            Shop smart with AI-personalized recommendations
          </p>
        </div>

        {/* Card Container */}
        <div className="glass-panel-dark rounded-3xl p-6 sm:p-8 shadow-2xl border border-white/10 backdrop-blur-2xl transition-all duration-300">
          
          {error && (
            <div className="mb-5 p-3.5 rounded-xl bg-rose-500/10 border border-rose-500/30 text-rose-300 text-xs flex items-start gap-2.5 animate-in fade-in duration-200">
              <AlertCircle className="w-4 h-4 text-rose-400 shrink-0 mt-0.5" />
              <div className="leading-relaxed font-medium">
                <span className="font-bold text-rose-400">✗ </span>{error}
              </div>
            </div>
          )}

          {/* ========================================================================= */}
          {/* STEP 1: EMAIL FIRST FLOW (Do not show Name/Password initially)             */}
          {/* ========================================================================= */}
          {step === 'email_input' && (
            <form onSubmit={handleCheckEmail} className="space-y-4 animate-in fade-in duration-200">
              <div>
                <label className="block text-xs font-semibold text-slate-300 mb-1.5">
                  Email Address
                </label>
                <div className="relative group">
                  <div className="absolute inset-y-0 left-0 pl-3.5 flex items-center pointer-events-none text-slate-500 group-focus-within:text-indigo-400 transition-colors">
                    <Mail className="w-4 h-4" />
                  </div>
                  <input
                    type="email"
                    required
                    autoFocus
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                    placeholder="Enter your email"
                    className="w-full pl-10 pr-4 py-3 bg-slate-800/80 hover:bg-slate-800 text-white placeholder-slate-500 text-sm rounded-xl border border-slate-700/80 focus:border-indigo-500 focus:ring-4 focus:ring-indigo-500/20 transition-all outline-hidden"
                  />
                </div>
              </div>

              <button
                type="submit"
                disabled={checkingEmail}
                className="w-full mt-2 py-3 px-4 rounded-xl ai-gradient-bg text-white font-bold text-sm shadow-lg shadow-indigo-600/30 hover:shadow-indigo-600/50 hover:opacity-95 active:scale-[0.98] transition-all flex items-center justify-center gap-2 disabled:opacity-50 cursor-pointer"
              >
                {checkingEmail ? (
                  <div className="w-5 h-5 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                ) : (
                  <>
                    <span>Continue</span>
                    <ArrowRight className="w-4 h-4" />
                  </>
                )}
              </button>

              <div className="pt-2 text-center text-xs text-slate-400">
                Already have an account?{' '}
                <Link to="/login" className="text-indigo-400 hover:text-indigo-300 font-semibold underline underline-offset-2 ml-1">
                  Sign in
                </Link>
              </div>
            </form>
          )}

          {/* ========================================================================= */}
          {/* CASE A: EMAIL EXISTS SCREEN                                                */}
          {/* ========================================================================= */}
          {step === 'email_exists' && (
            <div className="text-center space-y-5 animate-in fade-in zoom-in-95 duration-200">
              <div className="w-12 h-12 rounded-2xl bg-amber-500/20 border border-amber-500/30 text-amber-400 flex items-center justify-center mx-auto">
                <AlertCircle className="w-6 h-6" />
              </div>

              <div>
                <h3 className="text-lg font-bold text-white mb-1">Email Already Registered</h3>
                <p className="text-slate-300 text-xs sm:text-sm">
                  This email is already registered: <br />
                  <span className="font-semibold text-indigo-400">{email}</span>
                </p>
              </div>

              <div className="flex flex-col gap-3 pt-2">
                <Link
                  to={`/login?email=${encodeURIComponent(email)}`}
                  className="w-full py-3 px-4 rounded-xl ai-gradient-bg text-white font-bold text-sm shadow-lg shadow-indigo-600/30 hover:shadow-indigo-600/50 transition-all flex items-center justify-center gap-2"
                >
                  <span>Login</span>
                  <ArrowRight className="w-4 h-4" />
                </Link>

                <Link
                  to={`/forgot-password?email=${encodeURIComponent(email)}`}
                  className="w-full py-2.5 px-4 rounded-xl bg-slate-800/90 hover:bg-slate-800 border border-slate-700 text-slate-300 hover:text-white font-semibold text-xs transition-all flex items-center justify-center gap-2"
                >
                  <span>Forgot Password?</span>
                </Link>
              </div>

              <button
                type="button"
                onClick={() => setStep('email_input')}
                className="text-xs text-slate-400 hover:text-indigo-400 inline-flex items-center gap-1 cursor-pointer"
              >
                <ArrowLeft className="w-3.5 h-3.5" />
                <span>Use a different email</span>
              </button>
            </div>
          )}

          {/* ========================================================================= */}
          {/* CASE B: NEW EMAIL -> REVEAL FULL REGISTRATION FORM                        */}
          {/* ========================================================================= */}
          {step === 'account_details' && (
            <form onSubmit={handleRegister} className="space-y-4 animate-in fade-in duration-300">
              
              {/* Selected Email Chip */}
              <div className="flex items-center justify-between p-2.5 px-3.5 rounded-xl bg-slate-800/80 border border-slate-700/80 text-xs">
                <div className="flex items-center gap-2 text-slate-300 truncate">
                  <Mail className="w-3.5 h-3.5 text-indigo-400 shrink-0" />
                  <span className="truncate font-medium">{email}</span>
                </div>
                <button
                  type="button"
                  onClick={() => setStep('email_input')}
                  className="text-indigo-400 hover:text-indigo-300 font-semibold text-[11px] flex items-center gap-1 shrink-0 ml-2 cursor-pointer"
                >
                  <Edit2 className="w-3 h-3" />
                  <span>Change</span>
                </button>
              </div>

              {/* Full Name */}
              <div>
                <label className="block text-xs font-semibold text-slate-300 mb-1.5">
                  Full Name
                </label>
                <div className="relative group">
                  <div className="absolute inset-y-0 left-0 pl-3.5 flex items-center pointer-events-none text-slate-500 group-focus-within:text-indigo-400 transition-colors">
                    <User className="w-4 h-4" />
                  </div>
                  <input
                    type="text"
                    required
                    autoFocus
                    value={name}
                    onChange={(e) => setName(e.target.value)}
                    placeholder="Divya Sharma"
                    className="w-full pl-10 pr-4 py-2.5 bg-slate-800/80 hover:bg-slate-800 text-white placeholder-slate-500 text-sm rounded-xl border border-slate-700/80 focus:border-indigo-500 focus:ring-4 focus:ring-indigo-500/20 transition-all outline-hidden"
                  />
                </div>
              </div>

              {/* Password */}
              <div>
                <label className="block text-xs font-semibold text-slate-300 mb-1.5">
                  Password
                </label>
                <div className="relative group">
                  <div className="absolute inset-y-0 left-0 pl-3.5 flex items-center pointer-events-none text-slate-500 group-focus-within:text-indigo-400 transition-colors">
                    <Lock className="w-4 h-4" />
                  </div>
                  <input
                    type={showPassword ? 'text' : 'password'}
                    required
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    placeholder="e.g. Divya@123"
                    className="w-full pl-10 pr-10 py-2.5 bg-slate-800/80 hover:bg-slate-800 text-white placeholder-slate-500 text-sm rounded-xl border border-slate-700/80 focus:border-indigo-500 focus:ring-4 focus:ring-indigo-500/20 transition-all outline-hidden"
                  />
                  <button
                    type="button"
                    onClick={() => setShowPassword(!showPassword)}
                    className="absolute inset-y-0 right-0 pr-3.5 flex items-center text-slate-500 hover:text-slate-300 transition-colors cursor-pointer"
                  >
                    {showPassword ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
                  </button>
                </div>
              </div>

              {/* Reusable Live Password Strength Meter */}
              <PasswordStrengthMeter password={password} />

              {/* Confirm Password */}
              <div>
                <label className="block text-xs font-semibold text-slate-300 mb-1.5">
                  Confirm Password
                </label>
                <div className="relative group">
                  <div className="absolute inset-y-0 left-0 pl-3.5 flex items-center pointer-events-none text-slate-500 group-focus-within:text-indigo-400 transition-colors">
                    <Lock className="w-4 h-4" />
                  </div>
                  <input
                    type={showConfirmPassword ? 'text' : 'password'}
                    required
                    value={confirmPassword}
                    onChange={(e) => setConfirmPassword(e.target.value)}
                    placeholder="••••••••"
                    className="w-full pl-10 pr-10 py-2.5 bg-slate-800/80 hover:bg-slate-800 text-white placeholder-slate-500 text-sm rounded-xl border border-slate-700/80 focus:border-indigo-500 focus:ring-4 focus:ring-indigo-500/20 transition-all outline-hidden"
                  />
                  <button
                    type="button"
                    onClick={() => setShowConfirmPassword(!showConfirmPassword)}
                    className="absolute inset-y-0 right-0 pr-3.5 flex items-center text-slate-500 hover:text-slate-300 transition-colors cursor-pointer"
                  >
                    {showConfirmPassword ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
                  </button>
                </div>
              </div>

              {/* Create Account Button */}
              <button
                type="submit"
                disabled={registering}
                className="w-full mt-3 py-3 px-4 rounded-xl ai-gradient-bg text-white font-bold text-sm shadow-lg shadow-indigo-600/30 hover:shadow-indigo-600/50 hover:opacity-95 active:scale-[0.98] transition-all flex items-center justify-center gap-2 disabled:opacity-50 cursor-pointer"
              >
                {registering ? (
                  <div className="w-5 h-5 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                ) : (
                  <>
                    <span>Create Account</span>
                    <ArrowRight className="w-4 h-4" />
                  </>
                )}
              </button>

            </form>
          )}

        </div>

        {/* Footer Badges */}
        <div className="mt-6 flex items-center justify-center gap-6 text-slate-400 text-xs">
          <div className="flex items-center gap-1.5">
            <Lock className="w-4 h-4 text-emerald-400" />
            <span>Bcrypt Hashed</span>
          </div>
          <div className="flex items-center gap-1.5">
            <ShieldCheck className="w-4 h-4 text-indigo-400" />
            <span>Secure 6-Digit OTP</span>
          </div>
        </div>

      </div>
    </div>
  );
}
