import React, { useRef, useEffect } from 'react';

/**
 * Reusable 6-Digit OTP Input Component
 * Supports auto-focus, automatic tab advancement, backspace navigation, and clipboard paste.
 */
export default function OTPInput({ value = ['', '', '', '', '', ''], onChange, disabled = false }) {
  const inputRefs = useRef([]);

  useEffect(() => {
    // Focus first empty box
    const firstEmpty = value.findIndex((v) => !v);
    const indexToFocus = firstEmpty === -1 ? 0 : firstEmpty;
    inputRefs.current[indexToFocus]?.focus();
  }, []);

  const handleChange = (e, index) => {
    const val = e.target.value;
    if (val && !/^\d+$/.test(val)) return;

    const newOtp = [...value];
    newOtp[index] = val.substring(val.length - 1);
    onChange(newOtp);

    // Auto advance
    if (val && index < 5) {
      inputRefs.current[index + 1]?.focus();
    }
  };

  const handleKeyDown = (e, index) => {
    if (e.key === 'Backspace') {
      if (!value[index] && index > 0) {
        inputRefs.current[index - 1]?.focus();
      }
    }
  };

  const handlePaste = (e) => {
    e.preventDefault();
    const pastedData = e.clipboardData.getData('text').trim();
    if (/^\d{6}$/.test(pastedData)) {
      const digits = pastedData.split('');
      onChange(digits);
      inputRefs.current[5]?.focus();
    }
  };

  return (
    <div className="flex justify-between items-center gap-2 sm:gap-3" onPaste={handlePaste}>
      {value.map((digit, index) => (
        <input
          key={index}
          ref={(el) => (inputRefs.current[index] = el)}
          type="text"
          inputMode="numeric"
          maxLength={1}
          disabled={disabled}
          value={digit}
          onChange={(e) => handleChange(e, index)}
          onKeyDown={(e) => handleKeyDown(e, index)}
          className={`w-12 h-14 sm:w-13 sm:h-16 text-center text-xl sm:text-2xl font-extrabold text-white rounded-2xl border transition-all outline-hidden ${
            digit 
              ? 'border-indigo-500 bg-indigo-500/15 ring-4 ring-indigo-500/20' 
              : 'border-slate-700 bg-slate-800/80 hover:bg-slate-800 focus:border-indigo-500 focus:ring-4 focus:ring-indigo-500/20'
          }`}
        />
      ))}
    </div>
  );
}
