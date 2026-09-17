import React from 'react';
import { Biomarkers } from '../api/client';
import { Activity, Info } from 'lucide-react';

interface BiomarkersViewProps {
  biomarkers: Biomarkers;
}

export const BiomarkersView: React.FC<BiomarkersViewProps> = ({ biomarkers }) => {
  // Normal clinical benchmark thresholds from literature (Boersma et al., Max Little et al.)
  const jitterElevated = biomarkers.jitter_local_percent > 1.04;
  const shimmerElevated = biomarkers.shimmer_local_percent > 3.81;
  const hnrReduced = biomarkers.hnr_mean_db < 20.0;

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between border-b border-slate-100 pb-2">
        <h4 className="font-semibold text-slate-800 text-sm flex items-center gap-2">
          <Activity className="w-4 h-4 text-teal-600" />
          Extracted Acoustic Biomarkers
        </h4>
        <span className="text-[11px] text-slate-500 font-mono">Praat / Parselmouth Analysis</span>
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3">
        {/* Jitter Metric */}
        <div className={`p-3.5 rounded-xl border ${jitterElevated ? 'bg-amber-50/50 border-amber-200' : 'bg-slate-50/60 border-slate-200'}`}>
          <div className="flex items-center justify-between text-xs text-slate-500 mb-1">
            <span className="font-medium">Jitter (Local)</span>
            <span className={`px-1.5 py-0.5 rounded text-[10px] font-semibold ${jitterElevated ? 'bg-amber-100 text-amber-800' : 'bg-emerald-100 text-emerald-800'}`}>
              {jitterElevated ? 'Elevated' : 'Normal'}
            </span>
          </div>
          <div className="text-lg font-bold text-slate-900 font-mono">
            {biomarkers.jitter_local_percent.toFixed(2)}%
          </div>
          <p className="text-[11px] text-slate-500 mt-1">
            Normal: &lt; 1.04% | RAP: {biomarkers.jitter_rap_percent.toFixed(2)}%
          </p>
        </div>

        {/* Shimmer Metric */}
        <div className={`p-3.5 rounded-xl border ${shimmerElevated ? 'bg-amber-50/50 border-amber-200' : 'bg-slate-50/60 border-slate-200'}`}>
          <div className="flex items-center justify-between text-xs text-slate-500 mb-1">
            <span className="font-medium">Shimmer (Local)</span>
            <span className={`px-1.5 py-0.5 rounded text-[10px] font-semibold ${shimmerElevated ? 'bg-amber-100 text-amber-800' : 'bg-emerald-100 text-emerald-800'}`}>
              {shimmerElevated ? 'Elevated' : 'Normal'}
            </span>
          </div>
          <div className="text-lg font-bold text-slate-900 font-mono">
            {biomarkers.shimmer_local_percent.toFixed(2)}%
          </div>
          <p className="text-[11px] text-slate-500 mt-1">
            Normal: &lt; 3.81% | {biomarkers.shimmer_local_db.toFixed(2)} dB
          </p>
        </div>

        {/* HNR Metric */}
        <div className={`p-3.5 rounded-xl border ${hnrReduced ? 'bg-amber-50/50 border-amber-200' : 'bg-slate-50/60 border-slate-200'}`}>
          <div className="flex items-center justify-between text-xs text-slate-500 mb-1">
            <span className="font-medium">Harmonics-to-Noise</span>
            <span className={`px-1.5 py-0.5 rounded text-[10px] font-semibold ${hnrReduced ? 'bg-amber-100 text-amber-800' : 'bg-emerald-100 text-emerald-800'}`}>
              {hnrReduced ? 'Reduced' : 'Normal'}
            </span>
          </div>
          <div className="text-lg font-bold text-slate-900 font-mono">
            {biomarkers.hnr_mean_db.toFixed(1)} dB
          </div>
          <p className="text-[11px] text-slate-500 mt-1">
            Normal: &gt; 20 dB (PD often &lt; 15 dB)
          </p>
        </div>

        {/* Pitch (F0) Metric */}
        <div className="p-3.5 rounded-xl border bg-slate-50/60 border-slate-200">
          <div className="flex items-center justify-between text-xs text-slate-500 mb-1">
            <span className="font-medium">Pitch Mean (F0)</span>
            <span className="px-1.5 py-0.5 rounded text-[10px] font-semibold bg-slate-200 text-slate-700">
              Fundamental
            </span>
          </div>
          <div className="text-lg font-bold text-slate-900 font-mono">
            {biomarkers.f0_mean.toFixed(1)} Hz
          </div>
          <p className="text-[11px] text-slate-500 mt-1">
            Range: {biomarkers.f0_min.toFixed(0)} - {biomarkers.f0_max.toFixed(0)} Hz (σ: {biomarkers.f0_std.toFixed(1)})
          </p>
        </div>
      </div>

      <div className="p-3 bg-slate-50 rounded-lg text-slate-600 text-xs flex items-start gap-2 border border-slate-200">
        <Info className="w-4 h-4 text-teal-600 flex-shrink-0 mt-0.5" />
        <div className="space-y-1 text-[11px]">
          <p>
            <strong>Acoustic Interpretation:</strong> Jitter represents frequency instability across glottal cycles; Shimmer reflects amplitude variability from incomplete vocal fold adduction; HNR quantifies breathiness and glottal turbulence.
          </p>
        </div>
      </div>
    </div>
  );
};
