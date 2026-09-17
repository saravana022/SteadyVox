import React from 'react';
import { ScreeningResponse } from '../api/client';
import { BiomarkersView } from './BiomarkersView';
import { AlertTriangle, CheckCircle2, AlertOctagon, Cpu, Clock, FileAudio } from 'lucide-react';

interface ScreeningResultProps {
  result: ScreeningResponse;
  onReset: () => void;
}

export const ScreeningResult: React.FC<ScreeningResultProps> = ({ result, onReset }) => {
  const isParkinsons = result.prediction === 'parkinsons';
  const confidencePercent = (result.confidence * 100).toFixed(1);
  const probabilityPercent = (result.probability * 100).toFixed(1);

  return (
    <div className="space-y-6">
      {/* Mandatory Regulatory & Medical Disclaimer Alert */}
      <div className="bg-amber-50 border-l-4 border-amber-500 p-4 rounded-r-xl shadow-sm text-xs md:text-sm text-amber-900 flex items-start gap-3">
        <AlertTriangle className="w-5 h-5 flex-shrink-0 text-amber-600 mt-0.5" />
        <div className="space-y-1">
          <p className="font-bold text-amber-950 uppercase tracking-wide">
            Research Screening Tool Only — Not a Medical Diagnosis
          </p>
          <p className="text-xs text-amber-800 leading-relaxed">
            SteadyVox generates experimental acoustic screening predictions for exploratory and research triaging only.
            This result is <strong>not</strong> clinical advice, a diagnosis, or a confirmation of Parkinson's Disease.
            Always consult a board-certified neurologist or licensed healthcare provider for clinical evaluation.
          </p>
        </div>
      </div>

      {/* Main Prediction Card */}
      <div className="bg-white rounded-2xl border border-slate-200 p-6 sm:p-8 shadow-sm space-y-6">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-slate-100 pb-6">
          <div className="space-y-1">
            <div className="flex items-center gap-2">
              <span className="text-xs font-mono uppercase bg-slate-100 text-slate-600 px-2 py-0.5 rounded">
                Session ID: {result.session_id.slice(0, 8)}...
              </span>
              {result.patient_identifier && (
                <span className="text-xs font-mono uppercase bg-teal-50 text-teal-700 px-2 py-0.5 rounded border border-teal-200">
                  {result.patient_identifier}
                </span>
              )}
            </div>
            <h3 className="text-xl sm:text-2xl font-bold text-slate-900 tracking-tight">
              Screening Analysis Result
            </h3>
            <p className="text-xs text-slate-500">
              Analyzed file: <span className="font-mono text-slate-700">{result.original_filename}</span>
            </p>
          </div>

          <div className="flex items-center gap-2">
            <button
              onClick={onReset}
              className="px-4 py-2 border border-slate-300 hover:bg-slate-50 rounded-lg text-xs font-semibold text-slate-700 transition shadow-sm"
            >
              Screen Another Sample
            </button>
          </div>
        </div>

        {/* Prediction Status Badge & Score Meter */}
        <div className={`p-6 rounded-xl border flex flex-col md:flex-row items-start md:items-center justify-between gap-6 ${
          isParkinsons ? 'bg-rose-50/50 border-rose-200' : 'bg-emerald-50/50 border-emerald-200'
        }`}>
          <div className="flex items-start gap-4">
            <div className={`w-12 h-12 rounded-xl flex items-center justify-center flex-shrink-0 shadow-sm ${
              isParkinsons ? 'bg-rose-600 text-white' : 'bg-emerald-600 text-white'
            }`}>
              {isParkinsons ? <AlertOctagon className="w-7 h-7" /> : <CheckCircle2 className="w-7 h-7" />}
            </div>
            <div>
              <div className="text-xs font-semibold uppercase tracking-wider text-slate-500 mb-0.5">
                Screening Classification
              </div>
              <h2 className={`text-lg sm:text-xl font-bold ${
                isParkinsons ? 'text-rose-900' : 'text-emerald-900'
              }`}>
                {isParkinsons ? "Parkinson's Disease Indicators Detected" : "Typical Healthy Phonation Profile"}
              </h2>
              <p className="text-xs text-slate-600 mt-1 max-w-lg">
                {isParkinsons
                  ? "Vocal features exhibit acoustic perturbations, micro-tremors, and periodicity fluctuations consistent with Parkinsonian dysarthria patterns."
                  : "Acoustic characteristics display harmonic stability, consistent glottal closure, and perturbation metrics within normal normative ranges."}
              </p>
            </div>
          </div>

          <div className="flex flex-col sm:flex-row md:flex-col items-start md:items-end gap-3 w-full md:w-auto flex-shrink-0">
            <div className="text-right">
              <span className="text-xs text-slate-500 block">Confidence: <strong className="text-slate-900 font-mono">{confidencePercent}%</strong></span>
              <span className="text-xs text-slate-500 block">Risk Score: <strong className="text-slate-900 font-mono">{probabilityPercent}%</strong></span>
            </div>
            <div className="w-full sm:w-48 md:w-36 bg-slate-200 rounded-full h-2.5 overflow-hidden">
              <div
                className={`h-full transition-all duration-1000 ${isParkinsons ? 'bg-rose-600' : 'bg-emerald-600'}`}
                style={{ width: `${confidencePercent}%` }}
              />
            </div>
          </div>
        </div>

        {/* Audio Player if URL available */}
        {result.audio_url && (
          <div className="p-4 bg-slate-50 rounded-xl border border-slate-200 flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3">
            <div className="flex items-center gap-2 text-xs font-semibold text-slate-700">
              <FileAudio className="w-4 h-4 text-teal-600" />
              <span>Voice Phonation Playback</span>
            </div>
            <audio controls src={result.audio_url} className="w-full sm:w-80 h-9" />
          </div>
        )}

        {/* Biomarkers Panel */}
        <BiomarkersView biomarkers={result.biomarkers} />

        {/* Technical Inference Telemetry Metadata */}
        <div className="border-t border-slate-100 pt-4 flex flex-wrap items-center justify-between gap-4 text-[11px] text-slate-500 font-mono">
          <div className="flex items-center gap-4">
            <span className="flex items-center gap-1">
              <Cpu className="w-3.5 h-3.5 text-slate-400" />
              Architecture: {result.model_architecture.toUpperCase()}
            </span>
            <span className="flex items-center gap-1">
              <Clock className="w-3.5 h-3.5 text-slate-400" />
              Inference Latency: {result.latency_ms.toFixed(1)} ms
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
