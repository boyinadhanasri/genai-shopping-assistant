import React, { useState, useEffect } from 'react';
import { useNavigate, useSearchParams, Link } from 'react-router-dom';
import { 
  Sparkles, 
  CheckCircle2, 
  AlertCircle, 
  ArrowRight, 
  ShieldCheck 
} from 'lucide-react';
import OTPInput from '../components/OTPInput';
import api from '../services/api';

export default function VerifyOTP() {
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();

  const email = searchParams.get('email') || '';
  const [otp, setOtp] = useState(['', '', '', '', '', '']);

  const [loading, setLoading] = useState(false);
  const [resending, setResending] = useState(false);
  const [countdown, setCountdown] = useState(30);
  const [canResend, setCanResend] = useState(false);

  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');

  // Countdown timer for Resend OTP
  useEffect(() => {
    let timer;
    if (countdown > 0) {
      timer = setInterval(() => setCountdown((c) => c - 1), 1000);
    } else {
      setCanResend(true);
    }
    return () => clearInterval(timer);
  }, [countdown]);

  const handleVerify = async (e) => {
    if (e) e.preventDefault();
    setError('');
    setSuccess('');

    const fullOtp = otp.join('');
    if (fullOtp.length !== 6) {
      setError('Please enter all 6 digits of the verification code.');
      return;
    }

    setLoading(true);
    try {
      await api.verifyOtp({ email, otp: fullOtp });
      setSuccess('Email verified successfully.');
      setTimeout(() => {
        navigate(`/login?email=${encodeURIComponent(email)}&verified=1`);
      }, 1200);
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

  const handleResend = async () => {
    if (!canResend || resending) return;
    setError('');
    setSuccess('');
    setResending(true);

    try {
      const res = await api.resendOtp(email);
      setCountdown(30);
      setCanResend(false);
      setOtp(['', '', '', '', '', '']);
      if (res.otp) {
        setSuccess(`New OTP generated: ${res.otp}`);
      } else {
        setSuccess('A new verification code has been sent.');
      }
    } catch (err) {
      setError(err.message || 'Could not resend code. Please try again.');
    } finally {
      setResending(false);
    }
  };

  const handleAutofill = (code) => {
    if (!code || code.length !== 6) return;
    setOtp(code.split(''));
  };

  return (
    <div className="min-h-screen relative flex items-center justify-center p-4 bg-slate-900 overflow-hidden font-sans">
      {/* Ambient Glows */}
      <div className="absolute top-1/4 -left-32 w-96 h-96 bg-indigo-600/30 rounded-full blur-[128px] pointer-events-none" />
      <div className="absolute bottom-1/4 -right-32 w-96 h-96 bg-purple-600/30 rounded-full blur-[128px] pointer-events-none" />

      <div className="relative z-10 w-full max-w-md my-8">
        
        {/* Brand Header */}
        <div className="text-center mb-6">
          <Link to="/" className="inline-flex items-center justify-center w-14 h-14 rounded-2xl ai-gradient-bg text-white shadow-xl shadow-indigo-500/30 mb-3 transform hover:scale-105 transition-transform">
            <Sparkles className="w-8 h-8 animate-pulse" />
          </Link>
          <h1 className="text-2xl sm:text-3xl font-extrabold text-white tracking-tight">
            Verify Your Email
          </h1>
          <p className="text-slate-400 text-xs sm:text-sm mt-1">
            Enter the 6-digit OTP sent to <br />
            <span className="text-indigo-400 font-semibold">{email || 'your email'}</span>
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

          {success && (
            <div className="mb-5 p-3.5 rounded-xl bg-emerald-500/10 border border-emerald-500/30 text-emerald-300 text-xs flex items-center justify-between gap-2.5 animate-in fade-in duration-200">
              <div className="flex items-center gap-2">
                <CheckCircle2 className="w-4 h-4 text-emerald-400 shrink-0" />
                <span className="font-semibold">{success}</span>
              </div>
              {success.includes('New OTP generated:') && (
                <button
                  type="button"
                  onClick={() => handleAutofill(success.split('New OTP generated:')[1].trim())}
                  className="px-2.5 py-1 rounded-lg bg-emerald-500/20 hover:bg-emerald-500/30 text-emerald-200 text-[11px] font-bold transition-colors cursor-pointer"
                >
                  Auto-fill
                </button>
              )}
            </div>
          )}

          {/* Dev Mode Terminal Tip */}
          <div className="mb-5 p-3 rounded-xl bg-indigo-500/10 border border-indigo-500/20 text-indigo-200 text-[11px] flex items-start gap-2">
            <span className="font-bold text-indigo-400 shrink-0">💡 Note:</span>
            <span>Check your running <strong>backend terminal</strong> for the 6-digit code (e.g., <code className="text-white bg-slate-800 px-1.5 py-0.5 rounded font-mono">🔑 VERIFICATION OTP CODE: XXXXXX</code>) or click <strong>Resend Code</strong> below.</span>
          </div>

          <form onSubmit={handleVerify} className="space-y-6">
            
            {/* Reusable OTP Input */}
            <div>
              <label className="block text-xs font-semibold text-slate-300 mb-3 text-center">
                Enter OTP
              </label>
              <OTPInput value={otp} onChange={setOtp} disabled={loading} />
            </div>

            {/* Verify Button */}
            <button
              type="submit"
              disabled={loading || otp.join('').length !== 6}
              className="w-full py-3 px-4 rounded-xl ai-gradient-bg text-white font-bold text-sm shadow-lg shadow-indigo-600/30 hover:shadow-indigo-600/50 hover:opacity-95 active:scale-[0.98] transition-all flex items-center justify-center gap-2 disabled:opacity-50 cursor-pointer"
            >
              {loading ? (
                <div className="w-5 h-5 border-2 border-white/30 border-t-white rounded-full animate-spin" />
              ) : (
                <>
                  <span>Verify</span>
                  <ArrowRight className="w-4 h-4" />
                </>
              )}
            </button>

            {/* Resend OTP Section with Countdown */}
            <div className="pt-2 text-center text-xs text-slate-400 flex items-center justify-center gap-1.5">
              <span>Didn't receive the code?</span>
              {canResend ? (
                <button
                  type="button"
                  onClick={handleResend}
                  disabled={resending}
                  className="text-indigo-400 hover:text-indigo-300 font-bold underline cursor-pointer inline-flex items-center gap-1"
                >
                  {resending ? 'Sending...' : 'Resend OTP'}
                </button>
              ) : (
                <span className="text-slate-500 font-medium">
                  Resend OTP in <span className="text-slate-400 font-bold">{countdown}s</span>
                </span>
              )}
            </div>

          </form>

        </div>

        {/* Footer Security Badges */}
        <div className="mt-6 flex items-center justify-center gap-6 text-slate-400 text-xs">
          <div className="flex items-center gap-1.5">
            <ShieldCheck className="w-4 h-4 text-emerald-400" />
            <span>10-Minute Expiry</span>
          </div>
        </div>

      </div>
    </div>
  );
}
