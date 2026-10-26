import React from 'react';
import { Mic, ShieldAlert, Cpu, Sparkles } from 'lucide-react';

export const ProcessSteps: React.FC = () => {
  const steps = [
    {
      num: '001',
      tag: 'Capture',
      title: 'Phonation Recording',
      description: 'Record a sustained vowel "aaah" for 3 to 5 seconds via standard smartphone or computer microphone in a quiet setting.',
      icon: Mic,
    },
    {
      num: '002',
      tag: 'Gatekeeper',
      title: 'Acoustic Quality Gate',
      description: 'Real-time pre-flight verification tests signal-to-noise ratio (>9 dB), clipping ratio, and speech duration to reject noisy audio.',
      icon: ShieldAlert,
    },
    {
      num: '003',
      tag: 'DSP Engine',
      title: 'Biomarker Extraction',
      description: 'Praat/Parselmouth algorithms extract fundamental frequency (F0), period perturbation (Jitter), amplitude perturbation (Shimmer), and HNR.',
      icon: Sparkles,
    },
    {
      num: '004',
      tag: 'Dual-Path',
      title: 'Dual-Path Neural Scoring',
      description: 'Primary real-data Tabular MLP classifies 22 biomarkers, while secondary CNN+BiLSTM evaluates time-frequency micro-tremor spectrograms.',
      icon: Cpu,
    },
  ];

  return (
    <section className="py-20 md:py-28 border-b border-border">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 space-y-12">
        <div className="max-w-2xl space-y-3">
          <span className="eyebrow block">Screening Architecture</span>
          <h2 className="text-3xl sm:text-4xl font-bold tracking-tight text-txt">
            How SteadyVox Works
          </h2>
          <p className="text-sm sm:text-base text-txt-muted">
            From acoustic waveform ingestion to multi-biomarker neural evaluation.
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          {steps.map((step) => {
            const Icon = step.icon;
            return (
              <div
                key={step.num}
                className="card-nixtio p-6 sm:p-7 flex flex-col justify-between space-y-6 relative overflow-hidden group"
              >
                <div className="flex items-center justify-between">
                  <span className="font-mono text-xs font-bold text-accent px-2 py-0.5 rounded border border-accent/20 bg-accent-subtle">
                    {step.num}
                  </span>
                  <span className="text-[11px] font-semibold uppercase tracking-wider text-txt-muted">
                    {step.tag}
                  </span>
                </div>

                <div className="space-y-2.5">
                  <h3 className="text-lg font-bold text-txt tracking-tight group-hover:text-accent transition">
                    {step.title}
                  </h3>
                  <p className="text-xs text-txt-muted leading-relaxed">
                    {step.description}
                  </p>
                </div>

                <div className="pt-2 flex items-center justify-end text-border group-hover:text-accent/60 transition">
                  <Icon className="w-5 h-5" />
                </div>
              </div>
            );
          })}
        </div>
      </div>
    </section>
  );
};
