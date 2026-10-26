import React from 'react';
import { ShieldCheck, AlertTriangle, X } from 'lucide-react';

interface ConsentModalProps {
  isOpen: boolean;
  onConsent: (retainAudio: boolean) => void;
  onCancel: () => void;
}

export const ConsentModal: React.FC<ConsentModalProps> = ({ isOpen, onConsent, onCancel }) => {
  const [retainAudio, setRetainAudio] = React.useState<boolean>(true);

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/70 backdrop-blur-sm animate-fade-in">
      <div 
        role="dialog"
        aria-labelledby="consent-title"
        className="w-full max-w-lg card-nixtio p-6 sm:p-8 bg-surface border border-border shadow-2xl relative space-y-6"
      >
        <button
          onClick={onCancel}
          aria-label="Close dialog"
          className="touch-target absolute top-4 right-4 text-txt-muted hover:text-txt p-2 rounded-lg"
        >
          <X className="w-5 h-5" />
        </button>

        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-xl bg-accent-subtle text-accent flex items-center justify-center border border-accent/20">
            <ShieldCheck className="w-5 h-5" />
          </div>
          <div>
            <span className="eyebrow block">Ethical Research & Privacy</span>
            <h2 id="consent-title" className="text-xl font-bold tracking-tight text-txt">
              Participant Information & Consent
            </h2>
          </div>
        </div>

        {/* Regulatory disclaimer */}
        <div className="p-4 rounded-xl bg-amber-500/10 border border-amber-500/20 text-xs text-amber-300 leading-relaxed space-y-1">
          <div className="flex items-center gap-1.5 font-bold uppercase tracking-wider text-amber-400">
            <AlertTriangle className="w-4 h-4 flex-shrink-0" />
            <span>Research Tool Only — Not a Medical Diagnosis</span>
          </div>
          <p>
            SteadyVox evaluates acoustic perturbations associated with Parkinsonian dysarthria. It does not replace clinical examination, neurological consultation, or neuroimaging.
          </p>
        </div>

        {/* Data processing disclosure */}
        <div className="space-y-3 text-xs text-txt-muted leading-relaxed">
          <p>
            By proceeding, you understand that your voice sample will be analyzed for vocal biomarkers (Jitter, Shimmer, HNR, F0 tremor).
          </p>
          <label className="flex items-start gap-3 p-3.5 rounded-xl border border-border bg-surface-2 cursor-pointer hover:border-border-hover transition">
            <input
              type="checkbox"
              checked={retainAudio}
              onChange={(e) => setRetainAudio(e.target.checked)}
              className="mt-0.5 w-4 h-4 rounded text-accent focus:ring-accent border-border"
            />
            <span className="text-xs text-txt">
              <strong>Retain de-identified audio recording</strong> to allow playback in your session history. You may delete your data at any time via the History tab.
            </span>
          </label>
        </div>

        <div className="flex flex-col sm:flex-row items-center gap-3 pt-2">
          <button
            type="button"
            onClick={() => onConsent(retainAudio)}
            className="w-full sm:w-auto flex-1 touch-target px-6 py-3 bg-accent hover:bg-accent-hover text-white text-xs font-semibold rounded-xl shadow-lg transition"
          >
            I Understand & Agree to Proceed
          </button>
          <button
            type="button"
            onClick={onCancel}
            className="w-full sm:w-auto touch-target px-5 py-3 border border-border hover:bg-surface-2 text-xs font-medium text-txt-muted hover:text-txt rounded-xl transition"
          >
            Decline
          </button>
        </div>
      </div>
    </div>
  );
};
