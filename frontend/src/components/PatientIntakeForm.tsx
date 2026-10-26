import React, { useState } from 'react';
import { User, Calendar, ArrowRight, AlertCircle } from 'lucide-react';
import { apiClient, PatientResponse } from '../api/client';

interface PatientIntakeFormProps {
  onComplete: (patient: PatientResponse) => void;
  initialPatient?: PatientResponse | null;
}

export const PatientIntakeForm: React.FC<PatientIntakeFormProps> = ({ onComplete, initialPatient }) => {
  const [name, setName] = useState(initialPatient?.name || '');
  const [age, setAge] = useState<string>(initialPatient?.age ? String(initialPatient.age) : '');
  const [gender, setGender] = useState(initialPatient?.gender || 'Male');
  const [consent, setConsent] = useState(true);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);

    const parsedAge = parseInt(age, 10);
    if (!name.trim()) {
      setError('Please provide a name, initials, or participant identifier.');
      return;
    }
    if (isNaN(parsedAge) || parsedAge < 18 || parsedAge > 110) {
      setError('Age must be between 18 and 110.');
      return;
    }
    if (!consent) {
      setError('Informed consent is mandatory before recording phonation.');
      return;
    }

    try {
      setSubmitting(true);
      const patient = await apiClient.createPatient({
        name: name.trim(),
        age: parsedAge,
        gender,
        consent,
      });
      onComplete(patient);
    } catch (err: any) {
      setError(err?.message || 'Failed to submit intake. Please try again.');
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className="card max-w-xl mx-auto shadow-2xl border border-[var(--border)] bg-[var(--surface)] p-6 sm:p-8 rounded-2xl">
      <div className="flex items-center space-x-3 mb-6 pb-4 border-b border-[var(--border)]">
        <div className="w-10 h-10 rounded-xl bg-[var(--accent)]/10 text-[var(--accent)] flex items-center justify-center font-bold">
          1
        </div>
        <div>
          <h2 className="text-xl font-bold text-[var(--text)] tracking-tight">Participant Intake & Consent</h2>
          <p className="text-xs text-[var(--text-muted)]">
            Step 1 of 3 • Identifying details are encrypted at rest with AES-256 Fernet.
          </p>
        </div>
      </div>

      {error && (
        <div className="mb-6 p-4 rounded-xl bg-red-500/10 border border-red-500/20 text-red-400 text-sm flex items-start space-x-3">
          <AlertCircle className="w-5 h-5 flex-shrink-0 mt-0.5" />
          <span>{error}</span>
        </div>
      )}

      <form onSubmit={handleSubmit} className="space-y-5">
        <div>
          <label className="block text-xs uppercase tracking-wider text-[var(--text-muted)] font-semibold mb-2">
            Participant Name / Pseudonym <span className="text-red-400">*</span>
          </label>
          <div className="relative">
            <User className="absolute left-3.5 top-1/2 -translate-y-1/2 w-4 h-4 text-[var(--text-muted)]" />
            <input
              type="text"
              required
              placeholder="e.g. Eleanor Vance or P-104"
              value={name}
              onChange={(e) => setName(e.target.value)}
              className="w-full pl-10 pr-4 py-3 min-h-[48px] rounded-xl bg-[var(--surface-2)] border border-[var(--border)] text-[var(--text)] focus:outline-none focus:border-[var(--accent)] text-sm transition-colors"
            />
          </div>
          <p className="text-[11px] text-[var(--text-muted)] mt-1.5">
            Never used in ML classifier features. Stored strictly with zero-knowledge field encryption.
          </p>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
          <div>
            <label className="block text-xs uppercase tracking-wider text-[var(--text-muted)] font-semibold mb-2">
              Age (Years) <span className="text-red-400">*</span>
            </label>
            <div className="relative">
              <Calendar className="absolute left-3.5 top-1/2 -translate-y-1/2 w-4 h-4 text-[var(--text-muted)]" />
              <input
                type="number"
                required
                min={18}
                max={110}
                placeholder="65"
                value={age}
                onChange={(e) => setAge(e.target.value)}
                className="w-full pl-10 pr-4 py-3 min-h-[48px] rounded-xl bg-[var(--surface-2)] border border-[var(--border)] text-[var(--text)] focus:outline-none focus:border-[var(--accent)] text-sm transition-colors"
              />
            </div>
            <p className="text-[11px] text-[var(--text-muted)] mt-1.5">Used for acoustic reference ranges.</p>
          </div>

          <div>
            <label className="block text-xs uppercase tracking-wider text-[var(--text-muted)] font-semibold mb-2">
              Biological Sex / Gender <span className="text-red-400">*</span>
            </label>
            <select
              value={gender}
              onChange={(e) => setGender(e.target.value)}
              className="w-full px-4 py-3 min-h-[48px] rounded-xl bg-[var(--surface-2)] border border-[var(--border)] text-[var(--text)] focus:outline-none focus:border-[var(--accent)] text-sm transition-colors"
            >
              <option value="Male">Male</option>
              <option value="Female">Female</option>
              <option value="Other">Other</option>
              <option value="Prefer not to say">Prefer not to say</option>
            </select>
            <p className="text-[11px] text-[var(--text-muted)] mt-1.5">Used for pitch (F0) normative baseline.</p>
          </div>
        </div>

        <div className="p-4 rounded-xl bg-[var(--surface-2)] border border-[var(--border)] space-y-3">
          <label className="flex items-start space-x-3 cursor-pointer">
            <input
              type="checkbox"
              checked={consent}
              onChange={(e) => setConsent(e.target.checked)}
              className="mt-1 w-4 h-4 rounded text-[var(--accent)] border-[var(--border)] focus:ring-[var(--accent)]"
            />
            <span className="text-xs text-[var(--text)] leading-relaxed">
              I understand this is an experimental research screening aid and <strong>not a medical diagnosis</strong>. 
              I consent to having my sustained vowel phonation evaluated for acoustic micro-perturbations.
            </span>
          </label>
        </div>

        <button
          type="submit"
          disabled={submitting}
          className="w-full py-3.5 px-6 min-h-[48px] rounded-xl bg-[var(--accent)] hover:opacity-90 text-white font-semibold text-sm flex items-center justify-center space-x-2 transition-all shadow-lg shadow-[var(--accent)]/20 disabled:opacity-50"
        >
          {submitting ? (
            <span>Securing & Registering...</span>
          ) : (
            <>
              <span>Proceed to Voice Recording</span>
              <ArrowRight className="w-4 h-4" />
            </>
          )}
        </button>
      </form>
    </div>
  );
};
