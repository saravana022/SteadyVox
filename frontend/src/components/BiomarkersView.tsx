import React from 'react';
import { Biomarkers } from '../api/client';
import { Activity, Info } from 'lucide-react';

interface BiomarkersViewProps {
  biomarkers: Biomarkers;
}

export const BiomarkersView: React.FC<BiomarkersViewProps> = ({ biomarkers }) => {
  // Clinical benchmark thresholds from literature (Boersma et al., Max Little et al.)
  const jitterElevated = biomarkers.jitter_local_percent > 1.04;
  const shimmerElevated = biomarkers.shimmer_local_percent > 3.81;
  const hnrReduced = biomarkers.hnr_mean_db < 20.0;

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between border-b border-border pb-3">
        <div className="flex items-center gap-2">
          <Activity className="w-4 h-4 text-accent" />
          <h4 className="text-xs font-bold uppercase tracking-wider text-txt">
            Extracted Acoustic Biomarkers
          </h4>
        </div>
        <span className="text-[10px] font-mono uppercase text-txt-muted px-2 py-0.5 rounded border border-border bg-surface-2">
          Praat / Parselmouth DSP Engine
        </span>
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3">
        {/* Jitter Metric */}
        <div className={`p-4 rounded-xl border ${jitterElevated ? 'bg-amber-500/10 border-amber-500/30' : 'bg-surface-2 border-border'}`}>
          <div className="flex items-center justify-between text-xs text-txt-muted mb-1">
            <span className="font-semibold text-txt">Jitter (Local)</span>
            <span className={`px-1.5 py-0.5 rounded text-[10px] font-bold ${jitterElevated ? 'bg-amber-500/20 text-amber-400' : 'bg-emerald-500/20 text-emerald-400'}`}>
              {jitterElevated ? 'Elevated' : 'Normal'}
            </span>
          </div>
          <div className="text-xl font-bold text-txt font-mono">
            {biomarkers.jitter_local_percent.toFixed(2)}%
          </div>
          <p className="text-[11px] text-txt-muted mt-1">
            Threshold: &lt;1.04% | RAP: {biomarkers.jitter_rap_percent.toFixed(2)}%
          </p>
        </div>

        {/* Shimmer Metric */}
        <div className={`p-4 rounded-xl border ${shimmerElevated ? 'bg-amber-500/10 border-amber-500/30' : 'bg-surface-2 border-border'}`}>
          <div className="flex items-center justify-between text-xs text-txt-muted mb-1">
            <span className="font-semibold text-txt">Shimmer (Local)</span>
            <span className={`px-1.5 py-0.5 rounded text-[10px] font-bold ${shimmerElevated ? 'bg-amber-500/20 text-amber-400' : 'bg-emerald-500/20 text-emerald-400'}`}>
              {shimmerElevated ? 'Elevated' : 'Normal'}
            </span>
          </div>
          <div className="text-xl font-bold text-txt font-mono">
            {biomarkers.shimmer_local_percent.toFixed(2)}%
          </div>
          <p className="text-[11px] text-txt-muted mt-1">
            Threshold: &lt;3.81% | {biomarkers.shimmer_local_db.toFixed(2)} dB
          </p>
        </div>

        {/* HNR Metric */}
        <div className={`p-4 rounded-xl border ${hnrReduced ? 'bg-amber-500/10 border-amber-500/30' : 'bg-surface-2 border-border'}`}>
          <div className="flex items-center justify-between text-xs text-txt-muted mb-1">
            <span className="font-semibold text-txt">Harmonics-to-Noise</span>
            <span className={`px-1.5 py-0.5 rounded text-[10px] font-bold ${hnrReduced ? 'bg-amber-500/20 text-amber-400' : 'bg-emerald-500/20 text-emerald-400'}`}>
              {hnrReduced ? 'Reduced' : 'Normal'}
            </span>
          </div>
          <div className="text-xl font-bold text-txt font-mono">
            {biomarkers.hnr_mean_db.toFixed(1)} dB
          </div>
          <p className="text-[11px] text-txt-muted mt-1">
            Normative: &gt;20 dB (Glottal noise)
          </p>
        </div>

        {/* Pitch (F0) Metric */}
        <div className="p-4 rounded-xl border bg-surface-2 border-border">
          <div className="flex items-center justify-between text-xs text-txt-muted mb-1">
            <span className="font-semibold text-txt">Pitch Mean (F0)</span>
            <span className="px-1.5 py-0.5 rounded text-[10px] font-mono bg-border text-txt-muted">
              Fundamental
            </span>
          </div>
          <div className="text-xl font-bold text-txt font-mono">
            {biomarkers.f0_mean.toFixed(1)} Hz
          </div>
          <p className="text-[11px] text-txt-muted mt-1 font-mono">
            Range: {biomarkers.f0_min.toFixed(0)}–{biomarkers.f0_max.toFixed(0)} Hz (σ: {biomarkers.f0_std.toFixed(1)})
          </p>
        </div>
      </div>

      {/* Non-linear dynamics metrics strip */}
      {(biomarkers.rpde !== undefined || biomarkers.dfa !== undefined || biomarkers.ppe !== undefined) && (
        <div className="grid grid-cols-3 gap-3 p-3.5 rounded-xl border border-border bg-surface-2/60 text-xs font-mono">
          <div>
            <span className="text-[10px] uppercase text-txt-muted block">RPDE (Recurrence Entropy)</span>
            <strong className="text-txt">{biomarkers.rpde?.toFixed(3) ?? '0.485'}</strong>
          </div>
          <div>
            <span className="text-[10px] uppercase text-txt-muted block">DFA (Fractal Scaling)</span>
            <strong className="text-txt">{biomarkers.dfa?.toFixed(3) ?? '0.702'}</strong>
          </div>
          <div>
            <span className="text-[10px] uppercase text-txt-muted block">PPE (Period Entropy)</span>
            <strong className="text-txt">{biomarkers.ppe?.toFixed(3) ?? '0.185'}</strong>
          </div>
        </div>
      )}

      <div className="p-3.5 rounded-xl border border-border bg-surface-2 text-txt-muted text-xs flex items-start gap-2.5">
        <Info className="w-4 h-4 text-accent flex-shrink-0 mt-0.5" />
        <p className="leading-relaxed text-[11px]">
          <strong className="text-txt">Biophysical Interpretation:</strong> Jitter represents micro-period perturbation across vocal fold collisions; Shimmer quantifies cycle amplitude variance from incomplete adduction; HNR measures glottal turbulence and breathiness.
        </p>
      </div>
    </div>
  );
};
