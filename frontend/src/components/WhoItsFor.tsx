import React from 'react';
import { User, Stethoscope, Microscope, CheckCircle2 } from 'lucide-react';

export const WhoItsFor: React.FC = () => {
  const audiences = [
    {
      title: 'Individuals & Families',
      subtitle: 'Early Exploration & Symptom Tracking',
      icon: User,
      bullets: [
        'Non-invasive 60-second home screening via standard laptop or phone microphone.',
        'Objective tracking of vocal stability changes over time.',
        'Exportable acoustic summary to share with your attending physician.',
      ],
    },
    {
      title: 'Neurologists & SLPs',
      subtitle: 'Objective Dysarthria Triaging',
      icon: Stethoscope,
      bullets: [
        'Standardized acoustic perturbations (Jitter, Shimmer, HNR) complementing MDS-UPDRS III.',
        'Early detection of subclinical phonatory tremor before gross rest tremor.',
        'Longitudinal phonation comparison across medication cycles.',
      ],
    },
    {
      title: 'Clinical Researchers',
      subtitle: 'Digital Biomarker Phenotyping',
      icon: Microscope,
      bullets: [
        'Reproducible DSP pipeline grounded in Praat/Parselmouth algorithms.',
        'Benchmarked against Oxford (Little et al.) and Istanbul clinical cohorts.',
        'Dual-path model architecture comparing real-data MLP with acoustic CNN-BiLSTM.',
      ],
    },
  ];

  return (
    <section className="py-20 md:py-28 border-b border-border">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 space-y-12">
        <div className="max-w-2xl space-y-3">
          <span className="eyebrow block">Clinical Applications</span>
          <h2 className="text-3xl sm:text-4xl font-bold tracking-tight text-txt">
            Designed for Collaborative Care
          </h2>
          <p className="text-sm sm:text-base text-txt-muted">
            Empowering individuals, clinicians, and researchers with objective vocal biomarkers.
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          {audiences.map((aud, idx) => {
            const Icon = aud.icon;
            return (
              <div
                key={idx}
                className="card-nixtio p-6 sm:p-8 flex flex-col justify-between space-y-6"
              >
                <div className="space-y-4">
                  <div className="w-10 h-10 rounded-xl bg-surface-2 border border-border flex items-center justify-center text-accent">
                    <Icon className="w-5 h-5" />
                  </div>
                  <div>
                    <h3 className="text-lg font-bold text-txt tracking-tight">
                      {aud.title}
                    </h3>
                    <p className="text-xs text-txt-muted mt-0.5">
                      {aud.subtitle}
                    </p>
                  </div>

                  <ul className="space-y-2.5 pt-2">
                    {aud.bullets.map((b, bIdx) => (
                      <li key={bIdx} className="flex items-start gap-2.5 text-xs text-txt-muted leading-relaxed">
                        <CheckCircle2 className="w-4 h-4 text-accent flex-shrink-0 mt-0.5" />
                        <span>{b}</span>
                      </li>
                    ))}
                  </ul>
                </div>
              </div>
            );
          })}
        </div>
      </div>
    </section>
  );
};
