import React, { useState } from 'react';
import { ScreeningResponse } from '../api/client';
import { BiomarkersView } from './BiomarkersView';
import {
  AlertTriangle,
  CheckCircle2,
  AlertOctagon,
  HelpCircle,
  Cpu,
  Clock,
  FileAudio,
  Download,
  Hash,
  ShieldCheck,
  RotateCcw,
  User,
  ChevronDown,
  ChevronUp,
  Activity,
  FileText,
} from 'lucide-react';

interface ScreeningResultProps {
  result: ScreeningResponse;
  onReset: () => void;
}

export const ScreeningResult: React.FC<ScreeningResultProps> = ({ result, onReset }) => {
  const [showAblation, setShowAblation] = useState(false);
  const risk = result.risk_level || 'uncertain';
  const probabilityPercent = (result.probability * 100).toFixed(1);
  const uncertaintyMarginPercent = (result.confidence * 100).toFixed(1);

  const getRiskConfig = (r: string) => {
    switch (r) {
      case 'low':
        return {
          title: 'Low Vocal Perturbation Profile',
          desc: 'Acoustic biomarkers (Jitter, Shimmer, Harmonics) are well within normative reference ranges for sustained phonation.',
          badgeClass: 'bg-emerald-500/15 border-emerald-500/30 text-emerald-400',
          meterClass: 'bg-emerald-500',
          icon: CheckCircle2,
          borderClass: 'border-emerald-500/30 bg-emerald-500/5',
        };
      case 'elevated':
        return {
          title: 'Elevated Risk Indicators Detected',
          desc: 'Acoustic micro-perturbations and harmonic noise metrics exceed normative cutoffs, characteristic of hypokinetic vocal changes.',
          badgeClass: 'bg-rose-500/15 border-rose-500/30 text-rose-400',
          meterClass: 'bg-rose-500',
          icon: AlertOctagon,
          borderClass: 'border-rose-500/30 bg-rose-500/5',
        };
      case 'ood':
        return {
          title: 'Signal Outside Calibrated Distribution (OOD)',
          desc: 'The acoustic profile differs substantially from the reference clinical training cohort. Please re-record a steady sustained /a/ in a quiet room.',
          badgeClass: 'bg-purple-500/15 border-purple-500/30 text-purple-400',
          meterClass: 'bg-purple-500',
          icon: AlertTriangle,
          borderClass: 'border-purple-500/30 bg-purple-500/5',
        };
      default:
        return {
          title: 'Uncertain / Borderline Phonation Profile',
          desc: 'Biomarkers lie in the intermediate margin between typical baseline and vocal micro-tremor. Longitudinal tracking or clinical consultation advised.',
          badgeClass: 'bg-amber-500/15 border-amber-500/30 text-amber-400',
          meterClass: 'bg-amber-500',
          icon: HelpCircle,
          borderClass: 'border-amber-500/30 bg-amber-500/5',
        };
    }
  };

  const riskConfig = getRiskConfig(risk);
  const StatusIcon = riskConfig.icon;

  const handleDownloadReport = () => {
    const reportData = JSON.stringify(result, null, 2);
    const blob = new Blob([reportData], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `SteadyVox-Report-${result.session_id.slice(0, 8)}.json`;
    a.click();
    URL.revokeObjectURL(url);
  };

  return (
    <div className="space-y-6 animate-fade-in">
      {/* Prominent Medical Disclaimer Banner */}
      <div className="p-4 rounded-xl border border-amber-500/30 bg-amber-500/10 text-amber-400 flex items-start gap-3 text-xs leading-relaxed">
        <AlertTriangle className="w-5 h-5 flex-shrink-0 text-amber-400 mt-0.5" />
        <div className="space-y-0.5">
          <strong className="block font-bold uppercase tracking-wider text-amber-300">
            Research Screening Tool Only — Not a Medical Diagnosis
          </strong>
          <p className="text-amber-300/80">
            SteadyVox computes calibrated statistical likelihoods for exploratory vocal screening. It is not an FDA-cleared diagnostic device and cannot diagnose Parkinson’s disease. Always consult a qualified neurologist for medical evaluation.
          </p>
        </div>
      </div>

      {/* Main Analysis Card */}
      <div className="card-nixtio p-6 sm:p-8 space-y-8">
        {/* Header Strip with Participant Details */}
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-border pb-6">
          <div className="space-y-1">
            <div className="flex flex-wrap items-center gap-2">
              <span className="font-mono text-xs uppercase px-2.5 py-0.5 rounded border border-border bg-surface-2 text-txt-muted">
                Session: {result.session_id.slice(0, 8)}
              </span>
              {result.patient_name && (
                <span className="font-mono text-xs px-2.5 py-0.5 rounded border border-accent/20 bg-accent-subtle text-accent flex items-center gap-1">
                  <User className="w-3 h-3" />
                  {result.patient_name}
                  {result.patient_age && ` (${result.patient_age}y${result.patient_gender ? `, ${result.patient_gender}` : ''})`}
                </span>
              )}
              {result.ood_status === 'out_of_distribution' && (
                <span className="font-mono text-xs uppercase px-2.5 py-0.5 rounded border border-purple-500/30 bg-purple-500/10 text-purple-400">
                  OOD Guard Tripped
                </span>
              )}
            </div>
            <h2 className="text-2xl font-bold tracking-tight text-txt pt-1">
              Voice Screening Assessment
            </h2>
            <p className="text-xs text-txt-muted">
              Source sample: <span className="font-mono text-txt">{result.original_filename}</span>
            </p>
          </div>

          <div className="flex items-center gap-3">
            <button
              onClick={handleDownloadReport}
              className="touch-target px-4 py-2 rounded-xl border border-border hover:border-border-hover bg-surface hover:bg-surface-2 text-xs font-semibold text-txt flex items-center gap-1.5 transition shadow-sm"
            >
              <Download className="w-3.5 h-3.5" /> Export JSON
            </button>
            <button
              onClick={onReset}
              className="touch-target px-4 py-2 rounded-xl bg-accent hover:bg-accent-hover text-white text-xs font-semibold flex items-center gap-1.5 transition shadow-md"
            >
              <RotateCcw className="w-3.5 h-3.5" /> New Analysis
            </button>
          </div>
        </div>

        {/* 3-Tier Risk Classification Banner */}
        <div className={`p-6 sm:p-7 rounded-2xl border flex flex-col md:flex-row items-start md:items-center justify-between gap-6 ${riskConfig.borderClass}`}>
          <div className="flex items-start gap-4">
            <div className="w-12 h-12 rounded-xl flex items-center justify-center flex-shrink-0 bg-surface border border-border shadow-sm">
              <StatusIcon className="w-6 h-6 text-txt" />
            </div>
            <div className="space-y-1">
              <div className="flex items-center gap-2">
                <span className="eyebrow">Risk Stratification</span>
                <span className={`text-[10px] font-mono font-bold uppercase px-2 py-0.5 rounded border ${riskConfig.badgeClass}`}>
                  {risk.toUpperCase()}
                </span>
              </div>
              <h3 className="text-xl font-bold text-txt tracking-tight">
                {riskConfig.title}
              </h3>
              <p className="text-xs text-txt-muted max-w-xl leading-relaxed">
                {riskConfig.desc}
              </p>
            </div>
          </div>

          <div className="flex flex-col items-start md:items-end gap-2 w-full md:w-auto flex-shrink-0 font-mono">
            <div className="text-xs text-txt-muted text-left md:text-right space-y-1">
              <div>
                Calibrated Probability: <strong className="text-txt text-base">{probabilityPercent}%</strong>
              </div>
              {result.confidence_interval && (
                <div className="text-[11px] text-txt-muted">
                  95% CI: [{ (result.confidence_interval[0] * 100).toFixed(1) }% – { (result.confidence_interval[1] * 100).toFixed(1) }%]
                </div>
              )}
              <div className="text-[10px] text-txt-muted">
                Uncertainty Margin: ±{uncertaintyMarginPercent}%
              </div>
            </div>
            <div className="w-full sm:w-48 bg-surface-2 rounded-full h-2.5 overflow-hidden border border-border mt-1">
              <div
                className={`h-full transition-all duration-1000 ${riskConfig.meterClass}`}
                style={{ width: `${Math.min(100, Math.max(0, Number(probabilityPercent)))}%` }}
              />
            </div>
            <div className="flex justify-between w-full sm:w-48 text-[9px] text-txt-muted px-0.5">
              <span>0% Low</span>
              <span>30%</span>
              <span>60%</span>
              <span>100% High</span>
            </div>
          </div>
        </div>

        {/* Dynamic Feature-Based Acoustic Explanation */}
        {result.explanation && (
          <div className="p-5 rounded-xl border border-border bg-surface-2/40 space-y-2">
            <div className="flex items-center gap-2 text-xs font-semibold text-txt">
              <FileText className="w-4 h-4 text-accent" />
              <span>Acoustic Perturbation Analysis</span>
            </div>
            <p className="text-xs text-txt-muted leading-relaxed font-sans">
              {result.explanation}
            </p>
          </div>
        )}

        {/* Primary Model Provenance */}
        <div className="p-4 rounded-xl border border-border bg-surface-2/60 space-y-2">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <Activity className="w-4 h-4 text-accent" />
              <span className="text-xs font-bold text-txt">
                {result.primary_model.name}
              </span>
            </div>
            <span className="text-[10px] font-mono uppercase bg-emerald-500/10 border border-emerald-500/20 text-emerald-400 px-2 py-0.5 rounded">
              Subject-Wise Validated
            </span>
          </div>
          <p className="text-[11px] text-txt-muted">
            {result.primary_model.provenance}
          </p>
          <div className="flex flex-wrap items-center justify-between gap-2 text-[11px] font-mono text-txt-muted pt-1 border-t border-border/50">
            <span>Method: {result.primary_model.architecture}</span>
            <span>Validation: {result.primary_model.validation_metric}</span>
          </div>
        </div>

        {/* Audio Player if URL available */}
        {result.audio_url && (
          <div className="p-4 rounded-xl border border-border bg-surface-2 flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3">
            <div className="flex items-center gap-2 text-xs font-semibold text-txt">
              <FileAudio className="w-4 h-4 text-accent" />
              <span>Playback Phonation Recording</span>
            </div>
            <audio controls src={result.audio_url} className="w-full sm:w-80 h-9" />
          </div>
        )}

        {/* Extracted Biomarkers Panel */}
        <BiomarkersView biomarkers={result.biomarkers} />

        {/* Quality Gate Telemetry Badge */}
        {result.quality_report && (
          <div className="p-4 rounded-xl border border-border bg-surface-2/40 text-xs text-txt-muted space-y-2 font-mono">
            <div className="flex items-center justify-between">
              <span className="text-txt font-semibold flex items-center gap-1.5">
                <ShieldCheck className="w-4 h-4 text-accent" />
                Acoustic Quality Inspection
              </span>
              <span className="text-emerald-400 text-[11px]">PASSED GATEKEEPER</span>
            </div>
            <div className="grid grid-cols-2 sm:grid-cols-4 gap-2 text-[11px] pt-1">
              <div>Duration: <strong className="text-txt">{result.quality_report.duration_seconds}s</strong></div>
              <div>Estimated SNR: <strong className="text-txt">{result.quality_report.snr_db} dB</strong></div>
              <div>Clipping: <strong className="text-txt">{(result.quality_report.clipping_ratio * 100).toFixed(2)}%</strong></div>
              <div>Silence: <strong className="text-txt">{(result.quality_report.silence_ratio * 100).toFixed(1)}%</strong></div>
            </div>
          </div>
        )}

        {/* Optional Secondary Model Ablation (Engineering View) */}
        {result.secondary_model && (
          <div className="border border-border/60 rounded-xl overflow-hidden bg-surface">
            <button
              onClick={() => setShowAblation(!showAblation)}
              className="w-full px-4 py-3 bg-surface-2/50 hover:bg-surface-2 flex items-center justify-between text-xs text-txt-muted transition"
            >
              <span className="font-mono">Engineering Inspection: Deep Learning Spectrogram Baseline (Ablation)</span>
              {showAblation ? <ChevronUp className="w-4 h-4" /> : <ChevronDown className="w-4 h-4" />}
            </button>
            {showAblation && (
              <div className="p-4 space-y-2 text-xs border-t border-border/60 bg-surface-2/20">
                <p className="text-[11px] text-txt-muted">
                  The secondary path uses a CNN+BiLSTM on mel-spectrograms. Because deep neural models trained on small cohorts risk overfitting acoustic channel characteristics, this secondary score is maintained solely for model ablation and divergence monitoring.
                </p>
                <div className="flex items-center justify-between font-mono text-[11px] pt-2">
                  <span>Architecture: {result.secondary_model.architecture}</span>
                  <span>Ablation Score: {(result.secondary_model.probability * 100).toFixed(1)}%</span>
                  {result.path_disagreement && (
                    <span className="text-amber-400">Path Divergence Noted</span>
                  )}
                </div>
              </div>
            )}
          </div>
        )}

        {/* Technical Inference Telemetry Metadata */}
        <div className="border-t border-border pt-4 flex flex-wrap items-center justify-between gap-4 text-[11px] text-txt-muted font-mono">
          <div className="flex flex-wrap items-center gap-4">
            <span className="flex items-center gap-1">
              <Cpu className="w-3.5 h-3.5 text-accent" />
              Pipeline: {result.primary_model.version}
            </span>
            <span className="flex items-center gap-1">
              <Clock className="w-3.5 h-3.5 text-accent" />
              Latency: {result.latency_ms.toFixed(1)} ms
            </span>
            <span className="flex items-center gap-1">
              <Hash className="w-3.5 h-3.5 text-txt-muted" />
              SHA-256: {result.audio_sha256?.slice(0, 12)}...
            </span>
          </div>
          <div>
            Timestamp: {new Date(result.created_at).toLocaleString()}
          </div>
        </div>
      </div>
    </div>
  );
};
