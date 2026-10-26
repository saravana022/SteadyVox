import React from 'react';
import { User, Stethoscope, Microscope, CheckCircle2 } from 'lucide-react';

export const WhoItsFor: React.FC = () => {
  const audiences = [
    {
      title: 'Individuals & Families',
      subtitle: 'Early Exploration & Symptom Tracking',
      icon: User,
      image: '/images/audience-individuals.webp',
      alt: 'Individuals and family members using non-invasive voice screening at home',
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
      image: '/images/audience-clinicians.webp',
      alt: 'Neurologists and speech-language pathologists examining objective dysarthria biomarkers',
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
      image: '/images/audience-researchers.webp',
      alt: 'Clinical neuroscientists and researchers phenotyping digital acoustic biomarkers',
      bullets: [
        'Reproducible DSP pipeline grounded in Praat/Parselmouth algorithms.',
        'Benchmarked against Oxford (Little et al.) and Istanbul clinical cohorts.',
        'Dual-path model architecture comparing calibrated Random Forest with acoustic CNN-BiLSTM.',
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
                className="card-nixtio overflow-hidden flex flex-col justify-between"
              >
                {/* Visual Header Image */}
                <div className="relative w-full h-48 sm:h-52 overflow-hidden border-b border-border bg-surface-2">
                  <img
                    src={aud.image}
                    alt={aud.alt}
                    width={1024}
                    height={1024}
                    loading="lazy"
                    className="w-full h-full object-cover transition-transform duration-500 hover:scale-105"
                  />
                  <div className="absolute inset-0 bg-gradient-to-t from-surface via-transparent to-transparent opacity-80" />
                  <div className="absolute bottom-3 left-4 w-9 h-9 rounded-xl bg-surface/90 backdrop-blur-md border border-border flex items-center justify-center text-accent shadow-md">
                    <Icon className="w-4 h-4" />
                  </div>
                </div>

                <div className="p-6 sm:p-7 space-y-4 flex-1 flex flex-col justify-between">
                  <div className="space-y-1">
                    <h3 className="text-lg font-bold text-txt tracking-tight">
                      {aud.title}
                    </h3>
                    <p className="text-xs text-txt-muted">
                      {aud.subtitle}
                    </p>

                    <ul className="space-y-2.5 pt-3">
                      {aud.bullets.map((b, bIdx) => (
                        <li key={bIdx} className="flex items-start gap-2.5 text-xs text-txt-muted leading-relaxed">
                          <CheckCircle2 className="w-4 h-4 text-accent flex-shrink-0 mt-0.5" />
                          <span>{b}</span>
                        </li>
                      ))}
                    </ul>
                  </div>
                </div>
              </div>
            );
          })}
        </div>
      </div>
    </section>
  );
};
