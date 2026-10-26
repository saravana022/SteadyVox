import React, { useState } from 'react';
import symptomsData from '../data/symptoms.json';
import {
  Brain,
  Activity,
  Layers,
  Video,
  BookOpen,
  ExternalLink,
  CheckCircle2,
  Clock,
  Play,
  Stethoscope,
  Globe2,
  Gauge,
  Zap,
  Mic,
  Footprints,
  Edit3,
  Eye,
  Moon,
  Flame,
  HeartHandshake,
  BrainCircuit,
  Utensils,
  AlertCircle,
} from 'lucide-react';

interface VideoItem {
  id: string;
  title: string;
  titleTa?: string;
  source: string;
  language: 'en' | 'ta';
  duration: string;
  url: string;
  description: string;
  topics: string[];
}

interface ArticleItem {
  title: string;
  authors: string;
  journal: string;
  year: number;
  doi: string;
  url: string;
  takeaway: string;
  tag: string;
}

const SYMPTOM_ICONS: Record<string, React.ComponentType<{ className?: string }>> = {
  Activity,
  Gauge,
  Zap,
  Mic,
  Footprints,
  Edit3,
  Eye,
  Moon,
  Flame,
  HeartHandshake,
  BrainCircuit,
  Utensils,
};

export function ParkinsonKnowledgeHub() {
  const [activeSection, setActiveSection] = useState<'symptoms' | 'stages' | 'videos' | 'articles'>('symptoms');
  const [symptomCategory, setSymptomCategory] = useState<'all' | 'motor' | 'non-motor'>('all');
  const [videoLang, setVideoLang] = useState<'all' | 'en' | 'ta'>('all');
  const [selectedStage, setSelectedStage] = useState<number>(1);

  const stages = [
    {
      stage: 1,
      title: 'Stage 1: Initial Unilateral Phase',
      tagline: 'Mild symptoms affecting only one side of the body',
      description:
        'In the earliest clinical stage, symptoms are mild and typically affect only one side of the body (unilateral). Postural changes may begin subtly, but daily tasks are rarely disrupted.',
      signs: [
        'Mild tremor (often 4–6 Hz resting tremor) in one hand, arm, or leg',
        'Subtle facial expression flattening (hypomimia) on one side',
        'Slight micrographic handwriting (letters become progressively smaller)',
        'Unilateral arm swing reduction when walking',
      ],
      impact: 'Minimal functional disability. Independent in all activities of daily living (ADL).',
    },
    {
      stage: 2,
      title: 'Stage 2: Bilateral Involvement',
      tagline: 'Symptoms spread to both sides without balance impairment',
      description:
        'Symptoms advance to involve both sides of the body (bilateral) or midline structures (neck and trunk). Posture, gait, and vocal intensity begin showing noticeable alterations.',
      signs: [
        'Stiffness and rigidity in limbs on both sides of the body',
        'Hypophonia (reduced vocal loudness) and vocal pitch flattening (monotone)',
        'Stooped posture and decreased overall mobility',
        'Daily activities take visibly longer to complete',
      ],
      impact: 'Moderate inconvenience. Independent, but tasks require deliberate extra effort.',
    },
    {
      stage: 3,
      title: 'Stage 3: Mid-Stage Postural Instability',
      tagline: 'Balance compromise and increased fall susceptibility',
      description:
        'Regarded as the pivotal milestone dividing early and advanced disease. The defining clinical hallmark is the emergence of impaired postural reflexes (postural instability).',
      signs: [
        'Impaired balance during turning and walking; positive pull test',
        'Pronounced bradykinesia (slowed voluntary movement transitions)',
        'Freezing episodes when initiating steps or walking through doorways',
        'Difficulty dressing, handling utensils, or fine motor buttoning',
      ],
      impact: 'Significant functional impairment. The individual remains physically capable of independent living.',
    },
    {
      stage: 4,
      title: 'Stage 4: Severe Disability',
      tagline: 'Marked limitation; assistance needed for daily living',
      description:
        'Symptoms are severe and debilitating. While the individual may still be able to stand and walk unassisted, safe independent living is no longer feasible.',
      signs: [
        'Severely stooped posture and pronounced muscle rigidity',
        'High frequency of motor freezing and severe balance instability',
        'Speech volume is faint, breathy, and difficult to comprehend without repetition',
        'Substantial difficulty with grooming, bathing, and getting in/out of bed',
      ],
      impact: 'Requires regular daily caregiver assistance for safety and living.',
    },
    {
      stage: 5,
      title: 'Stage 5: Advanced Immobility',
      tagline: 'Wheelchair-bound or bedridden without constant support',
      description:
        'The most advanced stage of progression. Profound motor immobility prevents walking or standing unassisted. Around-the-clock specialized clinical and nursing support is essential.',
      signs: [
        'Inability to stand or walk without direct physical assistance',
        'Severely affected vocal phonation and marked oropharyngeal dysphagia',
        'Frequent hallucinations and cognitive decline may emerge',
        'Requires continuous 24-hour nursing supervision and transfer support',
      ],
      impact: 'Complete dependence on caregivers and specialized palliative or clinical nursing.',
    },
  ];

  const videos: VideoItem[] = [
    {
      id: 'v1',
      title: "Parkinson's Disease: Causes, Symptoms, Diagnosis & Treatment",
      source: 'Osmosis by Elsevier',
      language: 'en',
      duration: '11:20',
      url: 'https://www.youtube.com/watch?v=JwwbU_vI3X0',
      description:
        'A comprehensive animated medical breakdown covering substantia nigra dopaminergic loss, alpha-synuclein Lewy pathology, TRAP motor signs, and dopamine agonist treatments.',
      topics: ['Pathophysiology', 'Clinical Diagnosis', 'Pharmacology'],
    },
    {
      id: 'v2',
      title: "Understanding Parkinson's Disease: Symptoms, Causes & Science",
      source: 'Stanford Medicine Health',
      language: 'en',
      duration: '14:45',
      url: 'https://www.youtube.com/watch?v=kY31dK94_q4',
      description:
        'Stanford Health Care movement disorder neurologists explain motor vs non-motor signs, physical examination techniques, and modern therapeutic options.',
      topics: ['Clinical Signs', 'Patient Management', 'Movement Disorders'],
    },
    {
      id: 'v3',
      title: "Parkinson's 101: What You and Your Family Need to Know",
      source: 'The Michael J. Fox Foundation',
      language: 'en',
      duration: '08:35',
      url: 'https://www.youtube.com/watch?v=uD5o-9n3RzE',
      description:
        'An accessible patient-centered guide detailing early warning signs, research breakthroughs, and practical daily lifestyle adaptations.',
      topics: ['Patient Guide', 'Research Updates', 'Lifestyle Support'],
    },
    {
      id: 'v4',
      title: 'Speech and Voice Rehabilitation in Parkinson Disease (LSVT LOUD)',
      source: "Parkinson's Foundation Educational Series",
      language: 'en',
      duration: '06:40',
      url: 'https://www.youtube.com/watch?v=uK1XzM47_rQ',
      description:
        'Explains why Parkinson affects vocal cord adduction and respiratory drive, demonstrating clinical voice exercises to restore vocal loudness and clarity.',
      topics: ['Voice Biomarkers', 'Speech Therapy', 'LSVT LOUD'],
    },
    {
      id: 'v5',
      title: "பார்கின்சன் நோய் - அறிகுறிகள் மற்றும் சிகிச்சைகள் (Parkinson's Disease in Tamil)",
      titleTa: 'நடுக்க நோய் (Parkinson’s Disease) - முழு மருத்துவ விளக்கம்',
      source: 'Kauvery Hospital / Senior Neurologist',
      language: 'ta',
      duration: '10:15',
      url: 'https://www.youtube.com/watch?v=Xh0mY37B8zQ',
      description:
        'பார்கின்சன் நோய் எவ்வாறு மூளையின் டோபமைன் நரம்பணுக்களை பாதிக்கிறது, ஆரம்பகால கை நடுக்கம் மற்றும் நடை மாற்றங்கள் குறித்த விரிவான தமிழ் விளக்கம்.',
      topics: ['அறிகுறிகள்', 'டோபமைன் குறைபாடு', 'சிகிச்சை முறைகள்'],
    },
    {
      id: 'v6',
      title: "பார்கின்சன்ஸ் நோயை ஆரம்பத்திலேயே கண்டறிவது எப்படி? (Early Detection Guide)",
      titleTa: 'பார்கின்சன் ஆரம்ப அறிகுறிகள் & கவனிக்க வேண்டியவை',
      source: 'Apollo Hospitals Tamil / Dr. Neurologist',
      language: 'ta',
      duration: '08:50',
      url: 'https://www.youtube.com/watch?v=9_rX3KkQ12Y',
      description:
        'வயதானவர்களுக்கு ஏற்படும் கை நடுக்கம், பேச்சு மாற்றம் மற்றும் நடை நடுக்கத்தை ஆரம்பத்திலேயே பரிசோதிக்கும் முறைகள் பற்றிய மருத்துவ வழிகாட்டல்.',
      topics: ['ஆரம்ப பரிசோதனை', 'நரம்பியல் ஆலோசனை', 'பேச்சு மாற்றங்கள்'],
    },
    {
      id: 'v7',
      title: "பார்கின்சன் நோயில் குரல் மற்றும் பேச்சு பயிற்சி (Voice Therapy in Tamil)",
      titleTa: 'பார்கின்சன் பேச்சு குறைபாடு சரிசெய்யும் முறைகள்',
      source: 'Tamil Medical Health Hub / SLP Series',
      language: 'ta',
      duration: '07:30',
      url: 'https://www.youtube.com/watch?v=0k_2k3bW_wA',
      description:
        'குரல் வளம் குறைதல் (Hypophonia) மற்றும் வார்த்தை தெளிவின்மைக்கான தினசரி மூச்சு மற்றும் குரல் பயிற்சிகள் விளக்கம்.',
      topics: ['குரல் பயிற்சி', 'பேச்சு சிகிச்சை', 'மருத்துவ விழிப்புணர்வு'],
    },
  ];

  const articles: ArticleItem[] = [
    {
      title: 'Exploiting Nonlinear Recurrence and Fractal Scaling Properties for Voice Disorder Detection',
      authors: 'Little, M. A., McSharry, P. E., Roberts, S. J., Costello, D. A., Moroz, I. M.',
      journal: 'BioMedical Engineering OnLine, 6(1), 23',
      year: 2007,
      doi: '10.1186/1475-925X-6-23',
      url: 'https://doi.org/10.1186/1475-925X-6-23',
      takeaway:
        'Established that dysphonia measures (Jitter, Shimmer, Pitch Period Entropy) discriminate Parkinsonian voices from healthy controls with high accuracy.',
      tag: 'Foundational Dataset',
    },
    {
      title: 'Acoustic Analysis for Early Detection of Parkinson’s Disease: A Systematic Review',
      authors: 'Moro-Velázquez, L., Gómez-García, J. A., Godino-Llorente, J. I., et al.',
      journal: 'Computer Methods and Programs in Biomedicine, 199, 105849',
      year: 2021,
      doi: '10.1016/j.cmpb.2020.105849',
      url: 'https://doi.org/10.1016/j.cmpb.2020.105849',
      takeaway:
        'Comprehensive survey confirming phonatory micro-tremor and harmonic degradation as robust non-invasive digital screening biomarkers.',
      tag: 'Systematic Review',
    },
    {
      title: 'MDS Clinical Diagnostic Criteria for Parkinson’s Disease',
      authors: 'Postuma, R. B., Berg, D., Stern, M., Poewe, W., et al.',
      journal: 'Movement Disorders, 30(12), 1591-1601',
      year: 2015,
      doi: '10.1002/mds.26424',
      url: 'https://doi.org/10.1002/mds.26424',
      takeaway:
        'Defines mandatory motor criteria (bradykinesia plus rest tremor or rigidity) while validating non-motor prodromal markers including hyposmia and RBD.',
      tag: 'Diagnostic Criteria',
    },
  ];

  const filteredVideos = videos.filter((v) => {
    if (videoLang === 'all') return true;
    return v.language === videoLang;
  });

  return (
    <section id="parkinson-overview" className="py-20 md:py-28 border-b border-border scroll-mt-24">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 space-y-12">
        {/* Section Header */}
        <div className="max-w-3xl space-y-3">
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full border border-border bg-surface text-xs font-semibold text-accent">
            <Brain className="w-3.5 h-3.5" />
            <span>Clinical Knowledge & Educational Hub</span>
          </div>
          <h2 className="text-3xl sm:text-5xl font-extrabold tracking-tight text-txt">
            Understanding Parkinson's Disease
          </h2>
          <p className="text-sm sm:text-base text-txt-muted leading-relaxed">
            A comprehensive clinical guide covering neurobiological mechanisms, Hoehn & Yahr progression stages,
            observable symptoms, curated videos in English and தமிழ், and foundational scientific literature.
          </p>
        </div>

        {/* Biology Highlight Banner */}
        <div className="card-nixtio p-6 sm:p-8 bg-gradient-to-br from-surface to-surface-2 border-border/80 relative overflow-hidden">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6 relative z-10">
            <div className="space-y-2">
              <span className="text-[10px] font-mono uppercase text-accent tracking-wider font-bold block">
                01 • Neurobiology
              </span>
              <h3 className="text-base font-bold text-txt">Dopamine Depletion</h3>
              <p className="text-xs text-txt-muted leading-relaxed">
                Degeneration of dopaminergic neurons in the substantia nigra pars compacta disrupts basal ganglia circuits,
                reducing neuromuscular control over phonatory and respiratory muscle groups.
              </p>
            </div>
            <div className="space-y-2">
              <span className="text-[10px] font-mono uppercase text-accent tracking-wider font-bold block">
                02 • Vocal Pathology
              </span>
              <h3 className="text-base font-bold text-txt">Hypokinetic Dysarthria</h3>
              <p className="text-xs text-txt-muted leading-relaxed">
                Rigidity in laryngeal intrinsic muscles causes incomplete vocal fold closure, leading to micro-tremors (4–7 Hz),
                increased frequency perturbation (jitter), amplitude instability (shimmer), and reduced HNR.
              </p>
            </div>
            <div className="space-y-2">
              <span className="text-[10px] font-mono uppercase text-accent tracking-wider font-bold block">
                03 • Research Triaging
              </span>
              <h3 className="text-base font-bold text-txt">Calibrated Research Screening</h3>
              <p className="text-xs text-txt-muted leading-relaxed">
                Acoustic analysis provides a rapid, non-invasive digital biomarker for exploratory screening and
                longitudinal research triaging prior to in-person neurological motor evaluation.
              </p>
            </div>
          </div>
        </div>

        {/* Sub-Navigation Switcher with solid backing to prevent bleed-through */}
        <div className="flex flex-wrap items-center gap-2 border-b border-border pb-4 bg-bg/90">
          <button
            onClick={() => setActiveSection('symptoms')}
            className={`touch-target px-4 py-2 rounded-xl text-xs font-bold flex items-center gap-2 transition ${
              activeSection === 'symptoms'
                ? 'bg-txt text-bg shadow-sm'
                : 'bg-surface border border-border text-txt-muted hover:text-txt'
            }`}
          >
            <Activity className="w-4 h-4" />
            <span>Symptoms Matrix</span>
          </button>
          <button
            onClick={() => setActiveSection('stages')}
            className={`touch-target px-4 py-2 rounded-xl text-xs font-bold flex items-center gap-2 transition ${
              activeSection === 'stages'
                ? 'bg-txt text-bg shadow-sm'
                : 'bg-surface border border-border text-txt-muted hover:text-txt'
            }`}
          >
            <Layers className="w-4 h-4" />
            <span>Hoehn & Yahr Stages (1–5)</span>
          </button>
          <button
            onClick={() => setActiveSection('videos')}
            className={`touch-target px-4 py-2 rounded-xl text-xs font-bold flex items-center gap-2 transition ${
              activeSection === 'videos'
                ? 'bg-txt text-bg shadow-sm'
                : 'bg-surface border border-border text-txt-muted hover:text-txt'
            }`}
          >
            <Video className="w-4 h-4" />
            <span>Video Guides (English & தமிழ்)</span>
          </button>
          <button
            onClick={() => setActiveSection('articles')}
            className={`touch-target px-4 py-2 rounded-xl text-xs font-bold flex items-center gap-2 transition ${
              activeSection === 'articles'
                ? 'bg-txt text-bg shadow-sm'
                : 'bg-surface border border-border text-txt-muted hover:text-txt'
            }`}
          >
            <BookOpen className="w-4 h-4" />
            <span>Research Articles & Literature</span>
          </button>
        </div>

        {/* SECTION 1: SYMPTOMS MATRIX */}
        {activeSection === 'symptoms' && (
          <div className="space-y-6 animate-fade-in">
            {/* Visual Symptoms Header Banner */}
            <div className="relative w-full h-44 sm:h-56 rounded-2xl overflow-hidden border border-border bg-surface-2 shadow-sm">
              <img
                src="/images/symptoms-banner.webp"
                alt="Motor vs. non-motor clinical symptom spectrum overview"
                width={1584}
                height={672}
                loading="lazy"
                className="w-full h-full object-cover"
              />
              <div className="absolute inset-0 bg-gradient-to-t from-surface via-surface/40 to-transparent" />
              <div className="absolute bottom-4 left-6 right-6">
                <span className="eyebrow block text-white/90">Clinical Taxonomy</span>
                <h3 className="text-lg sm:text-xl font-bold text-white drop-shadow-md">
                  Motor vs. Non-Motor Symptom Spectrum
                </h3>
              </div>
            </div>

            <div className="flex flex-wrap items-center justify-between gap-4">
              <div>
                <p className="text-xs text-txt-muted max-w-xl leading-relaxed">
                  Parkinson's manifests across both conspicuous motor features and prodromal non-motor markers.
                  Review the prevalence ranges and source citations below.
                </p>
              </div>
              <div className="flex items-center gap-1.5 bg-surface border border-border p-1 rounded-lg text-xs">
                <button
                  onClick={() => setSymptomCategory('all')}
                  className={`px-3 py-1 rounded-md font-semibold transition ${
                    symptomCategory === 'all' ? 'bg-surface-2 text-txt' : 'text-txt-muted hover:text-txt'
                  }`}
                >
                  All (12)
                </button>
                <button
                  onClick={() => setSymptomCategory('motor')}
                  className={`px-3 py-1 rounded-md font-semibold transition ${
                    symptomCategory === 'motor' ? 'bg-surface-2 text-txt' : 'text-txt-muted hover:text-txt'
                  }`}
                >
                  Motor (6)
                </button>
                <button
                  onClick={() => setSymptomCategory('non-motor')}
                  className={`px-3 py-1 rounded-md font-semibold transition ${
                    symptomCategory === 'non-motor' ? 'bg-surface-2 text-txt' : 'text-txt-muted hover:text-txt'
                  }`}
                >
                  Non-Motor (6)
                </button>
              </div>
            </div>

            {/* 12 Symptom Cards with Lucide Icons, Prevalence, Sources, and TODO Review Flag */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5">
              {symptomsData.symptoms
                .filter((s) => symptomCategory === 'all' || s.type === symptomCategory)
                .map((sym) => {
                  const SymptomIcon = SYMPTOM_ICONS[sym.icon] || Activity;
                  return (
                    <div
                      key={sym.id}
                      className={`card-nixtio p-5 space-y-3 border-border/80 transition flex flex-col justify-between ${
                        sym.type === 'motor' ? 'hover:border-accent/40' : 'hover:border-amber-500/40'
                      }`}
                    >
                      <div className="space-y-2.5">
                        <div className="flex items-center justify-between gap-2">
                          <div className="flex items-center gap-2">
                            <div className={`w-8 h-8 rounded-lg flex items-center justify-center ${
                              sym.type === 'motor' ? 'bg-accent-subtle text-accent' : 'bg-amber-500/10 text-amber-400'
                            }`}>
                              <SymptomIcon className="w-4 h-4" />
                            </div>
                            <span
                              className={`text-[10px] font-mono uppercase px-2 py-0.5 rounded border font-bold ${
                                sym.type === 'motor'
                                  ? 'bg-accent-subtle text-accent border-accent/20'
                                  : 'bg-amber-500/10 text-amber-400 border-amber-500/20'
                              }`}
                            >
                              {sym.type}
                            </span>
                          </div>

                          <span className="text-[11px] font-mono font-bold text-txt">
                            Prev: {sym.prevalence}
                          </span>
                        </div>

                        <div className="flex items-center gap-2">
                          <h4 className="text-sm font-bold text-txt">{sym.name}</h4>
                          {sym.early_indicator && (
                            <span className="text-[9px] font-mono uppercase bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 px-1.5 py-0.2 rounded font-semibold">
                              Early Sign
                            </span>
                          )}
                        </div>

                        <p className="text-xs text-txt-muted leading-relaxed">{sym.description}</p>
                      </div>

                      {/* Source Citation & Clinician Review Notice */}
                      <div className="pt-2.5 border-t border-border/50 text-[10px] text-txt-muted space-y-1">
                        <div className="truncate">
                          <strong>Source:</strong> {sym.source}
                        </div>
                        <div className="flex items-center justify-between gap-2 font-mono">
                          <span>Reviewed: {sym.last_reviewed}</span>
                          {sym.clinician_review_needed && (
                            <span className="text-amber-400 font-semibold flex items-center gap-1">
                              <AlertCircle className="w-2.5 h-2.5 flex-shrink-0" />
                              TODO: Clinician review pending
                            </span>
                          )}
                        </div>
                      </div>
                    </div>
                  );
                })}
            </div>

            <div className="p-4 rounded-xl border border-border bg-surface-2/40 text-[11px] text-txt-muted flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3">
              <div>
                <strong>Global Sources:</strong> {symptomsData.sources.join(' • ')}
              </div>
              <div className="font-mono text-txt-muted flex-shrink-0">
                Last reviewed: {symptomsData.last_reviewed}
              </div>
            </div>
          </div>
        )}

        {/* SECTION 2: HOEHN & YAHR CLINICAL STAGES */}
        {activeSection === 'stages' && (
          <div className="space-y-8 animate-fade-in">
            {/* Visual Stages Steps Banner */}
            <div className="relative w-full h-44 sm:h-56 rounded-2xl overflow-hidden border border-border bg-surface-2 shadow-sm">
              <img
                src="/images/stages-steps.webp"
                alt="Hoehn and Yahr five-stage disease progression scale illustration"
                width={1376}
                height={768}
                loading="lazy"
                className="w-full h-full object-cover"
              />
              <div className="absolute inset-0 bg-gradient-to-t from-surface via-surface/40 to-transparent" />
              <div className="absolute bottom-4 left-6 right-6">
                <span className="eyebrow block text-white/90">Progression Staging</span>
                <h3 className="text-lg sm:text-xl font-bold text-white drop-shadow-md">
                  Hoehn & Yahr Clinical Progression (Stages 1–5)
                </h3>
              </div>
            </div>

            <div>
              <p className="text-xs text-txt-muted max-w-xl">
                The internationally recognized 5-stage scale describing progression from early unilateral involvement to advanced immobility.
              </p>
            </div>

            {/* Stage Selector Pills */}
            <div className="grid grid-cols-5 gap-2 sm:gap-4">
              {stages.map((st) => (
                <button
                  key={st.stage}
                  onClick={() => setSelectedStage(st.stage)}
                  className={`p-3 sm:p-4 rounded-xl border text-center transition flex flex-col items-center justify-center gap-1 ${
                    selectedStage === st.stage
                      ? 'border-accent bg-accent/10 shadow-md ring-1 ring-accent'
                      : 'border-border bg-surface hover:bg-surface-2'
                  }`}
                >
                  <span className="text-xs font-mono font-bold text-txt-muted">STAGE</span>
                  <span className="text-xl sm:text-2xl font-black text-txt">{st.stage}</span>
                </button>
              ))}
            </div>

            {/* Selected Stage Detail Card */}
            {(() => {
              const current = stages.find((s) => s.stage === selectedStage) || stages[0];
              return (
                <div className="card-nixtio p-6 sm:p-8 space-y-6 bg-surface-2/60 border-accent/30">
                  <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3 border-b border-border pb-4">
                    <div>
                      <div className="text-[11px] font-mono uppercase text-accent font-bold tracking-wider">
                        Clinical Stage {current.stage} of 5
                      </div>
                      <h4 className="text-xl font-extrabold text-txt mt-1">{current.title}</h4>
                      <p className="text-xs text-txt-muted mt-0.5">{current.tagline}</p>
                    </div>
                    <span className="text-xs font-mono px-3 py-1 rounded-full border border-border bg-surface text-txt-muted">
                      Hoehn & Yahr v2.0
                    </span>
                  </div>

                  <p className="text-xs sm:text-sm text-txt leading-relaxed">{current.description}</p>

                  <div className="grid grid-cols-1 md:grid-cols-2 gap-6 pt-2">
                    <div className="space-y-3">
                      <span className="text-xs font-bold text-txt flex items-center gap-2">
                        <CheckCircle2 className="w-4 h-4 text-accent" />
                        Common Clinical Manifestations
                      </span>
                      <ul className="space-y-2">
                        {current.signs.map((sign, idx) => (
                          <li key={idx} className="text-xs text-txt-muted flex items-start gap-2">
                            <span className="text-accent font-mono font-bold">•</span>
                            <span>{sign}</span>
                          </li>
                        ))}
                      </ul>
                    </div>

                    <div className="space-y-3">
                      <span className="text-xs font-bold text-txt flex items-center gap-2">
                        <Stethoscope className="w-4 h-4 text-emerald-400" />
                        Functional Impact & Independence
                      </span>
                      <div className="p-4 rounded-xl border border-border bg-surface text-xs text-txt-muted leading-relaxed">
                        {current.impact}
                      </div>
                    </div>
                  </div>
                </div>
              );
            })()}
          </div>
        )}

        {/* SECTION 3: VIDEO GUIDES (ENGLISH & TAMIL) */}
        {activeSection === 'videos' && (
          <div className="space-y-6 animate-fade-in">
            <div className="flex flex-wrap items-center justify-between gap-4">
              <div>
                <h3 className="text-lg font-bold text-txt">Educational & Clinical Video Guides</h3>
                <p className="text-xs text-txt-muted">
                  Curated neurological lectures, voice therapy overviews, and patient awareness videos in English and Tamil.
                </p>
              </div>
              <div className="flex items-center gap-1.5 bg-surface border border-border p-1 rounded-lg text-xs">
                <button
                  onClick={() => setVideoLang('all')}
                  className={`px-3 py-1 rounded-md font-semibold transition ${
                    videoLang === 'all' ? 'bg-surface-2 text-txt' : 'text-txt-muted hover:text-txt'
                  }`}
                >
                  All ({videos.length})
                </button>
                <button
                  onClick={() => setVideoLang('en')}
                  className={`px-3 py-1 rounded-md font-semibold transition flex items-center gap-1.5 ${
                    videoLang === 'en' ? 'bg-surface-2 text-txt' : 'text-txt-muted hover:text-txt'
                  }`}
                >
                  <Globe2 className="w-3.5 h-3.5" /> English (4)
                </button>
                <button
                  onClick={() => setVideoLang('ta')}
                  className={`px-3 py-1 rounded-md font-semibold transition flex items-center gap-1.5 ${
                    videoLang === 'ta' ? 'bg-surface-2 text-txt' : 'text-txt-muted hover:text-txt'
                  }`}
                >
                  <span>தமிழ் (Tamil - 3)</span>
                </button>
              </div>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              {filteredVideos.map((vid) => (
                <div
                  key={vid.id}
                  className="card-nixtio overflow-hidden flex flex-col justify-between border-border/80 hover:border-accent/40 transition group"
                >
                  {/* Video Cover Image with HTML Language Badge */}
                  <div className="relative w-full h-44 overflow-hidden bg-surface-2 border-b border-border">
                    <img
                      src={vid.language === 'ta' ? '/images/video-cover-ta.webp' : '/images/video-cover-en.webp'}
                      alt={`Video lecture cover: ${vid.title}`}
                      width={1376}
                      height={768}
                      loading="lazy"
                      className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-500"
                    />
                    <div className="absolute inset-0 bg-gradient-to-t from-surface via-transparent to-transparent opacity-80" />
                    
                    {/* Persistent Live HTML Language Badge */}
                    <div className="absolute top-3 left-3 flex items-center gap-1.5">
                      <span
                        className={`text-[10px] font-mono uppercase px-2.5 py-1 rounded-full font-bold shadow-md ${
                          vid.language === 'ta'
                            ? 'bg-amber-500 text-slate-950 border border-amber-400'
                            : 'bg-accent text-white border border-accent/40'
                        }`}
                      >
                        {vid.language === 'ta' ? 'தமிழ் (Tamil)' : 'English'}
                      </span>
                    </div>

                    <div className="absolute bottom-3 right-3 flex items-center gap-1 text-[11px] font-mono text-white bg-slate-950/70 px-2 py-0.5 rounded-md backdrop-blur-sm">
                      <Clock className="w-3 h-3" /> {vid.duration}
                    </div>
                  </div>

                  <div className="p-5 flex-1 flex flex-col justify-between space-y-4">
                    <div className="space-y-2">
                      <h4 className="text-sm font-bold text-txt group-hover:text-accent transition line-clamp-2">
                        {vid.title}
                      </h4>

                      {vid.titleTa && (
                        <p className="text-xs text-accent font-medium">{vid.titleTa}</p>
                      )}

                      <p className="text-xs text-txt-muted leading-relaxed line-clamp-3">
                        {vid.description}
                      </p>

                      <div className="flex flex-wrap gap-1.5 pt-1">
                        {vid.topics.map((t, tIdx) => (
                          <span
                            key={tIdx}
                            className="text-[10px] px-2 py-0.5 rounded-full border border-border bg-surface-2 text-txt-muted"
                          >
                            {t}
                          </span>
                        ))}
                      </div>
                    </div>

                    <div className="pt-3 border-t border-border flex items-center justify-between gap-2">
                      <span className="text-[11px] font-medium text-txt-muted truncate">{vid.source}</span>
                      <a
                        href={vid.url}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="touch-target px-3.5 py-1.5 rounded-lg bg-surface-2 hover:bg-accent hover:text-white text-txt text-xs font-semibold flex items-center gap-1.5 transition flex-shrink-0"
                      >
                        <Play className="w-3.5 h-3.5 fill-current" />
                        <span>Watch</span>
                      </a>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* SECTION 4: RESEARCH ARTICLES & LITERATURE */}
        {activeSection === 'articles' && (
          <div className="space-y-6 animate-fade-in">
            {/* Visual Literature Banner */}
            <div className="relative w-full h-44 sm:h-56 rounded-2xl overflow-hidden border border-border bg-surface-2 shadow-sm">
              <img
                src="/images/literature.webp"
                alt="Peer-reviewed Parkinson voice biomarker literature and clinical evidence"
                width={1200}
                height={896}
                loading="lazy"
                className="w-full h-full object-cover"
              />
              <div className="absolute inset-0 bg-gradient-to-t from-surface via-surface/40 to-transparent" />
              <div className="absolute bottom-4 left-6 right-6">
                <span className="eyebrow block text-white/90">Clinical Evidence Base</span>
                <h3 className="text-lg sm:text-xl font-bold text-white drop-shadow-md">
                  Peer-Reviewed Publications & Telemonitoring Literature
                </h3>
              </div>
            </div>

            <div>
              <p className="text-xs text-txt-muted">
                Key peer-reviewed papers on Parkinson's disease pathophysiology, acoustic speech biomarkers, and telemonitoring.
              </p>
            </div>

            <div className="space-y-4">
              {articles.map((art, idx) => (
                <div
                  key={idx}
                  className="card-nixtio p-5 sm:p-6 space-y-3 border-border/80 hover:border-accent/40 transition"
                >
                  <div className="flex flex-wrap items-center justify-between gap-2">
                    <span className="text-[10px] font-mono uppercase bg-accent-subtle text-accent px-2 py-0.5 rounded border border-accent/20 font-bold">
                      {art.tag}
                    </span>
                    <span className="text-xs font-mono text-txt-muted">{art.year}</span>
                  </div>

                  <h4 className="text-base font-bold text-txt">{art.title}</h4>
                  <p className="text-xs text-txt-muted font-medium">{art.authors} — <em className="text-txt">{art.journal}</em></p>

                  <div className="p-3.5 rounded-xl border border-border bg-surface-2 text-xs text-txt leading-relaxed">
                    <strong className="text-accent">Core Finding:</strong> {art.takeaway}
                  </div>

                  <div className="pt-2 flex items-center justify-between gap-3 text-xs">
                    <span className="font-mono text-txt-muted truncate text-[11px]">DOI: {art.doi}</span>
                    <a
                      href={art.url}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="text-accent hover:underline flex items-center gap-1 font-semibold flex-shrink-0"
                    >
                      <span>Read Publication</span>
                      <ExternalLink className="w-3.5 h-3.5" />
                    </a>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    </section>
  );
}
