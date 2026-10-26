import React from 'react';
import { Volume2, Repeat, BookOpen } from 'lucide-react';

export const VoiceTasksGrid: React.FC = () => {
  const tasks = [
    {
      title: 'Sustained Vowel Phonation',
      task: 'Continuous /a/ or /o/',
      recommended: true,
      icon: Volume2,
      protocol: 'Take a normal breath and sustain "aaah" at conversational pitch for 3–5 seconds.',
      measures: 'Jitter (frequency instability), Shimmer (amplitude perturbation), Harmonics-to-Noise Ratio (HNR).',
    },
    {
      title: 'Rapid Syllable Repetition',
      task: 'DDK "pa-ta-ka" Diadochokinesis',
      recommended: false,
      icon: Repeat,
      protocol: 'Repeat "pa-ta-ka" as rapidly and rhythmically as possible in a single steady breath.',
      measures: 'Articulatory velocity, syllable repetition regularity, voice onset timing (VOT) coordination.',
    },
    {
      title: 'Standardized Passage Reading',
      task: 'Grandfather / Rainbow Passage',
      recommended: false,
      icon: BookOpen,
      protocol: 'Read a short phonetically balanced paragraph aloud at your standard conversational speaking rate.',
      measures: 'Speech rate, fundamental frequency range variation, pause frequency, and monopitch dysarthria.',
    },
  ];

  return (
    <section className="py-20 md:py-28 border-b border-border">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 space-y-12">
        <div className="flex flex-col md:flex-row md:items-end justify-between gap-6">
          <div className="max-w-2xl space-y-3">
            <span className="eyebrow block">Acoustic Protocols</span>
            <h2 className="text-3xl sm:text-4xl font-bold tracking-tight text-txt">
              Supported Phonation Tasks
            </h2>
            <p className="text-sm sm:text-base text-txt-muted">
              Standardized clinical voice tasks sensitive to Parkinsonian hypokinetic dysarthria.
            </p>
          </div>
          <div className="text-xs text-txt-muted font-mono bg-surface border border-border px-3 py-1.5 rounded-xl">
            Protocol: Recommended task is Sustained /a/
          </div>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          {tasks.map((t, idx) => {
            const Icon = t.icon;
            return (
              <div
                key={idx}
                className="card-nixtio p-6 sm:p-8 flex flex-col justify-between space-y-6 relative group"
              >
                <div className="space-y-4">
                  <div className="flex items-center justify-between">
                    <div className="w-10 h-10 rounded-xl bg-surface-2 border border-border flex items-center justify-center text-txt group-hover:border-accent/30 group-hover:text-accent transition">
                      <Icon className="w-5 h-5" />
                    </div>
                    {t.recommended && (
                      <span className="text-[11px] font-bold uppercase tracking-wider text-accent px-2.5 py-0.5 rounded-full border border-accent/20 bg-accent-subtle">
                        Primary Screening Task
                      </span>
                    )}
                  </div>

                  <div>
                    <h3 className="text-lg font-bold text-txt tracking-tight group-hover:text-accent transition">
                      {t.title}
                    </h3>
                    <span className="text-xs font-mono text-txt-muted block mt-0.5">
                      {t.task}
                    </span>
                  </div>

                  <p className="text-xs text-txt-muted leading-relaxed">
                    {t.protocol}
                  </p>
                </div>

                <div className="pt-4 border-t border-border/60 text-xs text-txt-muted space-y-1">
                  <span className="text-[10px] uppercase font-bold tracking-wider text-txt block">
                    Evaluated Markers:
                  </span>
                  <span>{t.measures}</span>
                </div>
              </div>
            );
          })}
        </div>
      </div>
    </section>
  );
};
