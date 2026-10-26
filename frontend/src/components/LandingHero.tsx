import React from 'react';
import { ArrowRight, ShieldAlert } from 'lucide-react';
import { HeroIllustration } from './HeroIllustration';

interface LandingHeroProps {
  onStartTest: () => void;
  onViewEvidence: () => void;
}

export const LandingHero: React.FC<LandingHeroProps> = ({ onStartTest, onViewEvidence }) => {
  return (
    <section className="relative pt-12 pb-20 md:pt-16 md:pb-28 overflow-hidden border-b border-border bg-gradient-to-b from-bg to-surface">
      <div className="relative max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 space-y-12">
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-12 items-center">
          {/* Hero Left Content */}
          <div className="lg:col-span-7 space-y-6">
            {/* Top Eyebrow Tag */}
            <div className="inline-flex items-center gap-2 px-3.5 py-1.5 rounded-full border border-border bg-surface/80 backdrop-blur-md shadow-sm">
              <span className="w-2 h-2 rounded-full bg-accent animate-pulse" />
              <span className="text-[11px] font-semibold tracking-wider uppercase text-txt-muted">
                Calibrated Clinical Acoustic Biomarkers • Research Screener
              </span>
            </div>

            {/* Hero Headline and Subhead */}
            <div className="space-y-4">
              <h1 className="text-4xl sm:text-6xl font-extrabold tracking-tight text-txt leading-[1.08]">
                Screen Parkinson's Voice Markers in Seconds.
              </h1>
              <p className="text-base sm:text-lg text-txt-muted leading-relaxed max-w-2xl font-normal">
                Non-invasive analysis of sustained vowel phonation (<strong className="text-txt">/a/</strong>). SteadyVox isolates 16 clinical Praat acoustic perturbations—jitter, shimmer, and harmonics-to-noise ratio—calibrated via subject-wise cross-validation with out-of-distribution protection.
              </p>
            </div>

            {/* CTA Buttons */}
            <div className="flex flex-wrap items-center gap-4 pt-2">
              <button
                type="button"
                onClick={onStartTest}
                className="touch-target px-8 py-4 bg-accent hover:bg-accent-hover text-white text-sm font-semibold rounded-2xl shadow-xl shadow-accent/20 transition-all hover:scale-[1.02] flex items-center gap-2.5"
              >
                <span>Start Voice Analysis</span>
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

            {/* Non-Diagnostic Disclaimer Pill */}
            <div className="flex items-center gap-2 text-xs text-txt-muted pt-1">
              <ShieldAlert className="w-4 h-4 text-amber-400 flex-shrink-0" />
              <span>Investigational screening aid only — does not substitute for neurological diagnosis.</span>
            </div>
          </div>

          {/* Hero Right Graphic */}
          <div className="lg:col-span-5 flex justify-center">
            <HeroIllustration className="w-full" />
          </div>
        </div>

        {/* Verified Honest Metrics Strip (from model_metrics.json & Little et al. Oxford Cohort) */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 pt-8 border-t border-border">
          <div className="p-4 rounded-xl border border-border/60 bg-surface/40">
            <div className="text-2xl sm:text-3xl font-extrabold text-txt tracking-tight font-mono">
              70–90%
            </div>
            <p className="text-xs text-txt-muted mt-1 leading-snug">
              of PD patients develop voice changes (hypophonia, dysarthria) during disease course
            </p>
          </div>

          <div className="p-4 rounded-xl border border-border/60 bg-surface/40">
            <div className="text-2xl sm:text-3xl font-extrabold text-txt tracking-tight font-mono">
              0.7188
            </div>
            <p className="text-xs text-txt-muted mt-1 leading-snug">
              Subject-wise Leave-One-Group-Out ROC-AUC on real clinical Oxford cohort
            </p>
          </div>

          <div className="p-4 rounded-xl border border-border/60 bg-surface/40">
            <div className="text-2xl sm:text-3xl font-extrabold text-txt tracking-tight font-mono">
              89.6%
            </div>
            <p className="text-xs text-txt-muted mt-1 leading-snug">
              Cross-validated specificity on healthy controls with balanced Platt scaling
            </p>
          </div>

          <div className="p-4 rounded-xl border border-border/60 bg-surface/40">
            <div className="text-2xl sm:text-3xl font-extrabold text-txt tracking-tight font-mono">
              16
            </div>
            <p className="text-xs text-txt-muted mt-1 leading-snug">
              Praat MDVP acoustic features with 1:1 training-to-inference DSP parity
            </p>
          </div>
        </div>
      </div>
    </section>
  );
};
