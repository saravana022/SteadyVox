import React, { useState } from 'react';
import { ChevronDown, AlertTriangle } from 'lucide-react';

export const FAQAccordion: React.FC = () => {
  const [openIdx, setOpenIdx] = useState<number | null>(0);

  const faqs = [
    {
      q: 'Is SteadyVox a medical diagnosis for Parkinson\'s Disease?',
      a: 'No. SteadyVox is strictly an investigational research screening tool. It quantifies acoustic dysphonia and micro-tremor patterns that correlate with hypokinetic dysarthria. It cannot diagnose Parkinson\'s Disease or rule it out. Any screening result must be interpreted by a board-certified neurologist alongside clinical neurological motor examinations.',
      warning: true,
    },
    {
      q: 'Is my voice recording stored or private?',
      a: 'Privacy and ethical consent are paramount. Before recording, you can choose whether or not to retain your de-identified audio file. If you decline retention, your audio is analyzed in-memory and immediately discarded. If retained, you can permanently erase your session record at any time using the Delete button in the History tab.',
    },
    {
      q: 'Which microphones and audio formats produce the most reliable results?',
      a: 'Any standard headset or quiet-room smartphone/laptop microphone works well. For uploads, SteadyVox supports standard WAV, MP3, FLAC, and WebM files. The built-in Acoustic Quality Gate automatically inspects clipping and background signal-to-noise ratio (>9 dB) to guarantee acoustic validity.',
    },
    {
      q: 'How accurate is the screening model?',
      a: 'Our primary clinical model (Tabular MLP) was evaluated using 5-fold stratified cross-validation on the benchmark Oxford Parkinson\'s Disease Detection Dataset (Little et al., 2007), achieving an ROC-AUC of 0.8925 and F1-score of 0.9394. We transparently report synthetic benchmark numbers as ablation baselines and never claim synthetic performance as clinical efficacy.',
    },
    {
      q: 'What is the difference between the primary and secondary models?',
      a: 'The Primary Model (Tabular MLP) processes 22 gold-standard Praat acoustic biomarkers (Jitter, Shimmer, HNR, RPDE) trained on real clinical patient cohorts. The Secondary Model (CNN+BiLSTM) analyzes continuous 2D Log Mel-Spectrograms to detect temporal micro-tremor oscillations (4–7 Hz) across spectrogram frames.',
    },
  ];

  return (
    <section className="py-20 md:py-28 border-b border-border">
      <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 space-y-10">
        <div className="space-y-3">
          <span className="eyebrow block">Frequently Asked Questions</span>
          <h2 className="text-3xl sm:text-4xl font-bold tracking-tight text-txt">
            Scientific & Clinical FAQ
          </h2>
          <p className="text-sm text-txt-muted">
            Key details on clinical boundaries, algorithmic validation, and data privacy.
          </p>
        </div>

        <div className="space-y-4">
          {faqs.map((faq, idx) => {
            const isOpen = openIdx === idx;
            return (
              <div
                key={idx}
                className="card-nixtio overflow-hidden transition-all"
              >
                <button
                  type="button"
                  onClick={() => setOpenIdx(isOpen ? null : idx)}
                  aria-expanded={isOpen}
                  className="touch-target w-full px-6 py-5 flex items-center justify-between text-left gap-4"
                >
                  <span className="text-sm sm:text-base font-bold text-txt">
                    {faq.q}
                  </span>
                  <ChevronDown
                    className={`w-5 h-5 text-txt-muted flex-shrink-0 transition-transform duration-200 ${
                      isOpen ? 'rotate-180 text-accent' : ''
                    }`}
                  />
                </button>

                {isOpen && (
                  <div className="px-6 pb-6 pt-1 text-xs sm:text-sm text-txt-muted leading-relaxed border-t border-border/50 animate-fade-in space-y-3">
                    {faq.warning && (
                      <div className="flex items-center gap-2 p-2.5 rounded-lg bg-amber-500/10 border border-amber-500/20 text-amber-400 font-semibold text-xs">
                        <AlertTriangle className="w-4 h-4 flex-shrink-0" />
                        <span>Research screening tool only — not a clinical diagnosis.</span>
                      </div>
                    )}
                    <p>{faq.a}</p>
                  </div>
                )}
              </div>
            );
          })}
        </div>
      </div>
    </section>
  );
};
