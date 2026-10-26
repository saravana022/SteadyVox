import React from 'react';
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
} from 'lucide-react';

interface ScreeningResultProps {
  result: ScreeningResponse;
  onReset: () => void;
}

export const ScreeningResult: React.FC<ScreeningResultProps> = ({ result, onReset }) => {
  const risk = result.risk_level || 'uncertain';
  const confidencePercent = (result.confidence * 100).toFixed(1);
  const probabilityPercent = (result.probability * 100).toFixed(1);

  const getRiskConfig = (r: string) => {
    switch (r) {
      case 'low':
        return {
          title: 'Low Probability of Vocal Dysarthria',
          desc: 'Acoustic perturbation and harmonics exhibit high stability within normative healthy ranges.',
          badgeClass: 'bg-emerald-500/15 border-emerald-500/30 text-emerald-400',
          meterClass: 'bg-emerald-500',
          icon: CheckCircle2,
          borderClass: 'border-emerald-500/30 bg-emerald-500/5',
        };
      case 'elevated':
        return {
          title: 'Elevated Risk Indicators Detected',
          desc: 'Acoustic feature perturbations, micro-tremors, and glottal turbulence correlate with hypokinetic dysarthria patterns.',
          badgeClass: 'bg-rose-500/15 border-rose-500/30 text-rose-400',
          meterClass: 'bg-rose-500',
          icon: AlertOctagon,
          borderClass: 'border-rose-500/30 bg-rose-500/5',
        };
      default:
        return {
          title: 'Uncertain / Borderline Phonation Profile',
          desc: 'Acoustic biomarkers fall into an intermediate zone. Retesting with multiple sustained phonations or clinical SLP evaluation recommended.',
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
            SteadyVox generates investigational acoustic screening scores for exploratory clinical triaging only. This output is not a diagnosis. Consult a board-certified neurologist for comprehensive medical examination.
          </p>
        </div>
      </div>

      {/* Main Analysis Card */}
      <div className="card-nixtio p-6 sm:p-8 space-y-8">
        {/* Header Strip */}
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-border pb-6">
          <div className="space-y-1">
            <div className="flex flex-wrap items-center gap-2">
              <span className="font-mono text-xs uppercase px-2.5 py-0.5 rounded border border-border bg-surface-2 text-txt-muted">
                Session: {result.session_id.slice(0, 8)}
              </span>
              {result.patient_identifier && (
                <span className="font-mono text-xs uppercase px-2.5 py-0.5 rounded border border-accent/20 bg-accent-subtle text-accent">
                  {result.patient_identifier}
                </span>
              )}
              <span className="font-mono text-[11px] text-txt-muted px-2 py-0.5 rounded border border-border bg-surface-2">
                Req: {result.request_id?.slice(0, 8)}
              </span>
            </div>
            <h2 className="text-2xl font-bold tracking-tight text-txt pt-1">
              Phonation Screening Report
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
            <div className="text-xs text-txt-muted text-left md:text-right">
              <div>Probability Score: <strong className="text-txt text-sm">{probabilityPercent}%</strong></div>
              <div>Confidence Margin: <strong className="text-txt text-sm">{confidencePercent}%</strong></div>
            </div>
            <div className="w-full sm:w-44 bg-surface-2 rounded-full h-2 overflow-hidden border border-border">
              <div
                className={`h-full transition-all duration-1000 ${riskConfig.meterClass}`}
                style={{ width: `${probabilityPercent}%` }}
              />
            </div>
          </div>
        </div>

        {/* Dual-Path Model Disclosures */}
        <div className="space-y-3">
          <span className="eyebrow block">Dual-Path Model Transparency</span>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {/* Primary Model */}
            <div className="p-4 rounded-xl border border-border bg-surface-2/60 space-y-2">
              <div className="flex items-center justify-between">
                <span className="text-xs font-bold text-txt">
                  {result.primary_model.name}
                </span>
                <span className="text-[10px] font-mono uppercase bg-emerald-500/10 border border-emerald-500/20 text-emerald-400 px-2 py-0.5 rounded">
                  Clinical Ground Truth
                </span>
              </div>
              <p className="text-[11px] text-txt-muted">
                {result.primary_model.provenance}
              </p>
              <div className="flex items-center justify-between text-[11px] font-mono text-txt-muted pt-1 border-t border-border/50">
                <span>Validation: {result.primary_model.validation_metric}</span>
                <strong className="text-txt">Risk: {(result.primary_model.probability * 100).toFixed(1)}%</strong>
              </div>
            </div>

            {/* Secondary Model */}
            <div className="p-4 rounded-xl border border-border bg-surface-2/60 space-y-2">
              <div className="flex items-center justify-between">
                <span className="text-xs font-bold text-txt">
                  {result.secondary_model.name}
                </span>
                <span className="text-[10px] font-mono uppercase bg-accent-subtle border border-accent/20 text-accent px-2 py-0.5 rounded">
                  Synthetic Benchmark
                </span>
              </div>
              <p className="text-[11px] text-txt-muted">
                {result.secondary_model.provenance}
              </p>
              <div className="flex items-center justify-between text-[11px] font-mono text-txt-muted pt-1 border-t border-border/50">
                <span>Validation: Ablation Baseline</span>
                <strong className="text-txt">Risk: {(result.secondary_model.probability * 100).toFixed(1)}%</strong>
              </div>
            </div>
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

        {/* Technical Inference Telemetry Metadata */}
        <div className="border-t border-border pt-4 flex flex-wrap items-center justify-between gap-4 text-[11px] text-txt-muted font-mono">
          <div className="flex flex-wrap items-center gap-4">
            <span className="flex items-center gap-1">
              <Cpu className="w-3.5 h-3.5 text-accent" />
              Model: {result.primary_model.version}
            </span>
            <span className="flex items-center gap-1">
              <Clock className="w-3.5 h-3.5 text-accent" />
              Total Latency: {result.latency_ms.toFixed(1)} ms
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
