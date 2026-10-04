import React from 'react';
import { Check, X } from 'lucide-react';

/**
 * Reusable Password Strength Meter & Live Rule Validator
 * Displays live checkmarks and a 3-tier strength meter (Weak, Medium, Strong).
 */
export default function PasswordStrengthMeter({ password = '' }) {
  const criteria = [
    { label: 'Minimum 8 characters', met: password.length >= 8 },
    { label: 'Uppercase letter (A-Z)', met: /[A-Z]/.test(password) },
    { label: 'Lowercase letter (a-z)', met: /[a-z]/.test(password) },
    { label: 'Number (0-9)', met: /[0-9]/.test(password) },
    { label: 'Special character (!@#$%...)', met: /[!@#$%^&*(),.?":{}|<>\-_+=[\]\\/`~;']/.test(password) },
  ];

  const metCount = criteria.filter((c) => c.met).length;

  // Strength Level
  let strengthLabel = 'Weak';
  let strengthColor = 'bg-rose-500';
  let textColor = 'text-rose-400';
  let barWidth = 'w-1/3';

  if (metCount >= 5) {
    strengthLabel = 'Strong';
    strengthColor = 'bg-emerald-500';
    textColor = 'text-emerald-400';
    barWidth = 'w-full';
  } else if (metCount >= 3) {
    strengthLabel = 'Medium';
    strengthColor = 'bg-amber-500';
    textColor = 'text-amber-400';
    barWidth = 'w-2/3';
  }

  if (!password) {
    return null;
  }

  return (
    <div className="p-3.5 rounded-2xl bg-slate-800/70 border border-slate-700/70 space-y-2.5 animate-in fade-in duration-200">
      {/* Strength Bar & Label */}
      <div className="flex items-center justify-between text-xs">
        <span className="text-slate-400 font-medium">Password Strength:</span>
        <span className={`font-bold ${textColor}`}>{strengthLabel}</span>
      </div>

      <div className="w-full h-1.5 bg-slate-700/80 rounded-full overflow-hidden">
        <div
          className={`h-full ${strengthColor} ${barWidth} rounded-full transition-all duration-300 ease-out`}
        />
      </div>

      {/* Criteria Checklist */}
      <div className="grid grid-cols-1 sm:grid-cols-2 gap-1.5 pt-1 text-[11px]">
        {criteria.map((item, idx) => (
          <div
            key={idx}
            className={`flex items-center gap-1.5 transition-colors duration-150 ${
              item.met ? 'text-emerald-400 font-medium' : 'text-slate-500'
            }`}
          >
            {item.met ? (
              <Check className="w-3.5 h-3.5 shrink-0 text-emerald-400" />
            ) : (
              <span className="w-3.5 h-3.5 rounded-full border border-slate-600 shrink-0 inline-block" />
            )}
            <span>{item.label}</span>
          </div>
        ))}
      </div>
    </div>
  );
}
