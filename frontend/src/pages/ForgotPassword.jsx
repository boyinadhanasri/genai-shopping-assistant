import React, { useState } from 'react';
import { useNavigate, useSearchParams, Link } from 'react-router-dom';
import { 
  Sparkles, 
  Mail, 
  Lock, 
  Eye, 
  EyeOff, 
  ArrowRight, 
  ArrowLeft,
  CheckCircle2, 
  AlertCircle,
  ShieldCheck
} from 'lucide-react';
import OTPInput from '../components/OTPInput';
import PasswordStrengthMeter from '../components/PasswordStrengthMeter';
import api from '../services/api';

export default function ForgotPassword() {
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();

  // Multi-step: 'enter_email' | 'enter_otp' | 'new_password' | 'done'
  const [step, setStep] = useState('enter_email');

  const [email, setEmail] = useState(searchParams.get('email') || '');
  const [otp, setOtp] = useState(['', '', '', '', '', '']);

  const [newPassword, setNewPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [showConfirmPassword, setShowConfirmPassword] = useState(false);

  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');

  // Password criteria check
  const isPasswordValid = 
    newPassword.length >= 8 &&
    /[A-Z]/.test(newPassword) &&
    /[a-z]/.test(newPassword) &&
    /[0-9]/.test(newPassword) &&
    /[!@#$%^&*(),.?":{}|<>\-_+=[\]\\/`~;']/.test(newPassword);

  // Step 1: Request Reset OTP
  const handleSendResetOtp = async (e) => {
    e.preventDefault();
    setError('');
    const cleanEmail = email.trim().toLowerCase();
    if (!cleanEmail) {
      setError('Please enter your email address.');
      return;
    }

    setLoading(true);
    try {
      await api.forgotPassword(cleanEmail);
      setStep('enter_otp');
    } catch (err) {
      // Step forward regardless for enumeration safety
      setStep('enter_otp');
    } finally {
      setLoading(false);
    }
  };

  // Step 2 & 3: Verify Reset OTP
  const handleVerifyResetOtp = async (e) => {
    e.preventDefault();
    setError('');

    const fullOtp = otp.join('');
    if (fullOtp.length !== 6) {
      setError('Please enter all 6 digits of the reset code.');
      return;
    }

    setLoading(true);
    try {
      await api.verifyResetOtp({
        email: email.trim().toLowerCase(),
        otp: fullOtp,
      });
      setStep('new_password');
    } catch (err) {
      const msg = err.message || 'Invalid OTP.';
      if (msg.toLowerCase().includes('expired')) {
        setError('OTP expired. Request a new OTP.');
      } else {
        setError('Invalid OTP.');
      }
    } finally {
      setLoading(false);
    }
  };

  // Step 4: Submit New Password
  const handleResetPassword = async (e) => {
    e.preventDefault();
    setError('');

    if (!newPassword) {
      setError('Password cannot be empty.');
      return;
    }
    if (newPassword !== confirmPassword) {
      setError('Passwords do not match.');
      return;
    }
    if (!isPasswordValid) {
      setError('Password must meet all complexity requirements.');
      return;
    }

    setLoading(true);
    try {
      await api.resetPassword({
        email: email.trim().toLowerCase(),
        otp: otp.join(''),
        new_password: newPassword,
        confirm_password: confirmPassword,
      });

      setSuccess('Password updated successfully.');
      setStep('done');
      setTimeout(() => {
        navigate(`/login?email=${encodeURIComponent(email)}`);
      }, 1500);
    } catch (err) {
      setError(err.message || 'Failed to update password.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen relative flex items-center justify-center p-4 bg-slate-900 overflow-hidden font-sans">
      {/* Background Glows */}
      <div className="absolute top-1/4 -left-32 w-96 h-96 bg-indigo-600/30 rounded-full blur-[128px] pointer-events-none" />
      <div className="absolute bottom-1/4 -right-32 w-96 h-96 bg-purple-600/30 rounded-full blur-[128px] pointer-events-none" />

      <div className="relative z-10 w-full max-w-md my-8">
        
        {/* Brand Header */}
        <div className="text-center mb-6">
          <Link to="/" className="inline-flex items-center justify-center w-14 h-14 rounded-2xl ai-gradient-bg text-white shadow-xl shadow-indigo-500/30 mb-3 transform hover:scale-105 transition-transform">
            <Sparkles className="w-8 h-8 animate-pulse" />
          </Link>
          <h1 className="text-2xl sm:text-3xl font-extrabold text-white tracking-tight">
            Reset Password
          </h1>
          <p className="text-slate-400 text-xs sm:text-sm mt-1">
            {step === 'enter_email' && 'Step 1: Enter your registered email'}
            {step === 'enter_otp' && 'Step 2: Enter the 6-digit OTP sent to your email'}
            {step === 'new_password' && 'Step 3: Create your new password'}
            {step === 'done' && 'Password successfully updated'}
          </p>
        </div>

        {/* Card */}
        <div className="glass-panel-dark rounded-3xl p-6 sm:p-8 shadow-2xl border border-white/10 backdrop-blur-2xl">
          
          {error && (
            <div className="mb-5 p-3.5 rounded-xl bg-rose-500/10 border border-rose-500/30 text-rose-300 text-xs flex items-center gap-2.5 animate-in fade-in duration-200">
              <AlertCircle className="w-4 h-4 text-rose-400 shrink-0" />
              <span>{error}</span>
            </div>
          )}

          {/* STEP 1: ENTER EMAIL */}
          {step === 'enter_email' && (
            <form onSubmit={handleSendResetOtp} className="space-y-4 animate-in fade-in duration-200">
              <div>
                <label className="block text-xs font-semibold text-slate-300 mb-1.5">
                  Registered Email Address
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
                    placeholder="name@example.com"
                    className="w-full pl-10 pr-4 py-2.5 bg-slate-800/80 hover:bg-slate-800 text-white placeholder-slate-500 text-sm rounded-xl border border-slate-700/80 focus:border-indigo-500 focus:ring-4 focus:ring-indigo-500/20 transition-all outline-hidden"
                  />
                </div>
              </div>

              <button
                type="submit"
                disabled={loading}
                className="w-full mt-2 py-3 px-4 rounded-xl ai-gradient-bg text-white font-bold text-sm shadow-lg shadow-indigo-600/30 hover:shadow-indigo-600/50 hover:opacity-95 active:scale-[0.98] transition-all flex items-center justify-center gap-2 disabled:opacity-50 cursor-pointer"
              >
                {loading ? (
                  <div className="w-5 h-5 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                ) : (
                  <>
                    <span>Send Reset OTP</span>
                    <ArrowRight className="w-4 h-4" />
                  </>
                )}
              </button>

              <div className="pt-2 text-center text-xs text-slate-400">
                <Link to="/login" className="text-indigo-400 hover:text-indigo-300 font-semibold inline-flex items-center gap-1">
                  <ArrowLeft className="w-3.5 h-3.5" />
                  <span>Return to Login</span>
                </Link>
              </div>
            </form>
          )}

          {/* STEP 2: VERIFY RESET OTP */}
          {step === 'enter_otp' && (
            <form onSubmit={handleVerifyResetOtp} className="space-y-5 animate-in fade-in duration-200">
              
              <div className="p-3.5 rounded-xl bg-indigo-500/10 border border-indigo-500/20 text-xs text-indigo-200 leading-relaxed">
                If an account exists for <span className="font-bold text-white">{email}</span>, a 6-digit reset code has been sent.
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-300 mb-3 text-center">
                  Enter 6-Digit OTP
                </label>
                <OTPInput value={otp} onChange={setOtp} disabled={loading} />
              </div>

              <button
                type="submit"
                disabled={loading || otp.join('').length !== 6}
                className="w-full py-3 px-4 rounded-xl ai-gradient-bg text-white font-bold text-sm shadow-lg shadow-indigo-600/30 hover:shadow-indigo-600/50 hover:opacity-95 active:scale-[0.98] transition-all flex items-center justify-center gap-2 disabled:opacity-50 cursor-pointer"
              >
                {loading ? (
                  <div className="w-5 h-5 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                ) : (
                  <>
                    <span>Verify Code</span>
                    <ArrowRight className="w-4 h-4" />
                  </>
                )}
              </button>

              <div className="pt-1 text-center text-xs text-slate-400">
                <button
                  type="button"
                  onClick={() => setStep('enter_email')}
                  className="text-slate-400 hover:text-indigo-400 inline-flex items-center gap-1 cursor-pointer"
                >
                  <ArrowLeft className="w-3.5 h-3.5" />
                  <span>Change email</span>
                </button>
              </div>
            </form>
          )}

          {/* STEP 3: CREATE NEW PASSWORD */}
          {step === 'new_password' && (
            <form onSubmit={handleResetPassword} className="space-y-4 animate-in fade-in duration-200">
              
              <div>
                <label className="block text-xs font-semibold text-slate-300 mb-1.5">
                  New Password
                </label>
                <div className="relative group">
                  <div className="absolute inset-y-0 left-0 pl-3.5 flex items-center pointer-events-none text-slate-500 group-focus-within:text-indigo-400 transition-colors">
                    <Lock className="w-4 h-4" />
                  </div>
                  <input
                    type={showPassword ? 'text' : 'password'}
                    required
                    autoFocus
                    value={newPassword}
                    onChange={(e) => setNewPassword(e.target.value)}
                    placeholder="e.g. Divya@123"
                    className="w-full pl-10 pr-10 py-2.5 bg-slate-800/80 hover:bg-slate-800 text-white placeholder-slate-500 text-sm rounded-xl border border-slate-700/80 focus:border-indigo-500 focus:ring-4 focus:ring-indigo-500/20 transition-all outline-hidden"
                  />
                  <button
                    type="button"
                    onClick={() => setShowPassword(!showPassword)}
                    className="absolute inset-y-0 right-0 pr-3.5 flex items-center text-slate-500 hover:text-slate-300 cursor-pointer"
                  >
                    {showPassword ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
                  </button>
                </div>
              </div>

              {/* Password Strength Meter */}
              <PasswordStrengthMeter password={newPassword} />

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
                    className="absolute inset-y-0 right-0 pr-3.5 flex items-center text-slate-500 hover:text-slate-300 cursor-pointer"
                  >
                    {showConfirmPassword ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
                  </button>
                </div>
              </div>

              <button
                type="submit"
                disabled={loading}
                className="w-full mt-2 py-3 px-4 rounded-xl ai-gradient-bg text-white font-bold text-sm shadow-lg shadow-indigo-600/30 hover:shadow-indigo-600/50 hover:opacity-95 active:scale-[0.98] transition-all flex items-center justify-center gap-2 disabled:opacity-50 cursor-pointer"
              >
                {loading ? (
                  <div className="w-5 h-5 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                ) : (
                  <>
                    <span>Update Password</span>
                    <ArrowRight className="w-4 h-4" />
                  </>
                )}
              </button>
            </form>
          )}

          {/* DONE */}
          {step === 'done' && (
            <div className="text-center py-4 space-y-3 animate-in fade-in zoom-in-95 duration-200">
              <div className="w-14 h-14 rounded-2xl bg-emerald-500/20 border border-emerald-500/30 text-emerald-400 flex items-center justify-center mx-auto">
                <CheckCircle2 className="w-7 h-7" />
              </div>
              <h3 className="text-lg font-bold text-white">Password Updated!</h3>
              <p className="text-xs text-slate-300">
                {success} Redirecting to login...
              </p>
            </div>
          )}

        </div>

        {/* Footer Badges */}
        <div className="mt-6 flex items-center justify-center gap-6 text-slate-400 text-xs">
          <div className="flex items-center gap-1.5">
            <ShieldCheck className="w-4 h-4 text-emerald-400" />
            <span>Password Reuse Prevention</span>
          </div>
        </div>

      </div>
    </div>
  );
}
