import React from 'react';
import { ArrowRight } from 'lucide-react';
import { WaveformCanvas } from './WaveformCanvas';

interface LandingHeroProps {
  onStartTest: () => void;
  onViewEvidence: () => void;
}

export const LandingHero: React.FC<LandingHeroProps> = ({ onStartTest, onViewEvidence }) => {
  return (
    <section className="relative pt-12 pb-20 md:pt-20 md:pb-32 overflow-hidden border-b border-border">
      {/* Background ambient Waveform Canvas */}
      <div className="absolute inset-0 pointer-events-none opacity-40 dark:opacity-30">
        <WaveformCanvas className="w-full h-full" />
      </div>

      <div className="relative max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 space-y-12">
        {/* Top Eyebrow Tag */}
        <div className="inline-flex items-center gap-2 px-3.5 py-1.5 rounded-full border border-border bg-surface/80 backdrop-blur-md shadow-sm">
          <span className="w-2 h-2 rounded-full bg-accent animate-pulse" />
          <span className="text-[11px] font-semibold tracking-wider uppercase text-txt-muted">
            Oxford Clinical Dataset & Deep Neural Acoustic Screening
          </span>
        </div>

        {/* Hero Headline and Subhead */}
        <div className="max-w-4xl space-y-6">
          <h1 className="text-4xl sm:text-6xl lg:text-7xl font-extrabold tracking-tight text-txt leading-[1.08]">
            Screen Parkinson's Voice Markers in Seconds.
          </h1>
          <p className="text-base sm:text-xl text-txt-muted leading-relaxed max-w-2xl font-normal">
            Clinical-grade acoustic perturbation analysis paired with deep neural networks to identify early vocal fold instability, micro-tremor, and glottal turbulence.
          </p>
        </div>

        {/* CTA Buttons */}
        <div className="flex flex-wrap items-center gap-4 pt-2">
          <button
            type="button"
            onClick={onStartTest}
            className="touch-target px-8 py-4 bg-accent hover:bg-accent-hover text-white text-sm font-semibold rounded-2xl shadow-xl shadow-accent/20 transition-all hover:scale-[1.02] flex items-center gap-2.5"
          >
            <span>Start Voice Screening</span>
            <ArrowRight className="w-4 h-4" />
          </button>
          <button
            type="button"
            onClick={onViewEvidence}
            className="touch-target px-6 py-4 border border-border hover:border-border-hover bg-surface hover:bg-surface-2 text-sm font-medium text-txt rounded-2xl transition shadow-sm"
          >
            Explore Scientific Evidence
          </button>
        </div>

        {/* Nixtio-inspired Minimal Stat Strip */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 pt-8 border-t border-border">
          <div className="p-4 rounded-xl border border-border/60 bg-surface/40">
            <div className="text-2xl sm:text-3xl font-extrabold text-txt tracking-tight font-mono">
              70–90%
            </div>
            <p className="text-xs text-txt-muted mt-1 leading-snug">
              of PD patients exhibit vocal changes before gross motor tremor
            </p>
          </div>

          <div className="p-4 rounded-xl border border-border/60 bg-surface/40">
            <div className="text-2xl sm:text-3xl font-extrabold text-txt tracking-tight font-mono">
              0.8925
            </div>
            <p className="text-xs text-txt-muted mt-1 leading-snug">
              ROC-AUC validation score on real clinical Oxford cohort
            </p>
          </div>

          <div className="p-4 rounded-xl border border-border/60 bg-surface/40">
            <div className="text-2xl sm:text-3xl font-extrabold text-txt tracking-tight font-mono">
              22
            </div>
            <p className="text-xs text-txt-muted mt-1 leading-snug">
              vocal perturbations: Jitter, Shimmer, HNR, RPDE, DFA, PPE
            </p>
          </div>

          <div className="p-4 rounded-xl border border-border/60 bg-surface/40">
            <div className="text-2xl sm:text-3xl font-extrabold text-txt tracking-tight font-mono">
              ~60 sec
            </div>
            <p className="text-xs text-txt-muted mt-1 leading-snug">
              rapid, non-invasive phonation screening workflow
            </p>
          </div>
        </div>
      </div>
    </section>
  );
};
