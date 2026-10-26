import { useState } from 'react';
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
        'Wheelchair or bed confinement',
        'Significant dysphagia (swallowing difficulties) requiring modified diet/care',
        'Non-motor complications including cognitive changes or hallucinations',
      ],
      impact: 'Complete dependence on caregivers and specialized palliative or clinical nursing.',
    },
  ];

  const videos: VideoItem[] = [
    // English Videos
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
    // Tamil Videos
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
        'வாசனை இழப்பு, தூக்க கோளாறுகள், மற்றும் குரல் மாற்றங்கள் போன்ற ஆரம்பகால அறிகுறிகளை சரியான நேரத்தில் அடையாளம் காண்பதன் முக்கியத்துவம்.',
      topics: ['ஆரம்பகால பரிசோதனை', 'குரல் மாற்றங்கள்', 'நரம்பியல்'],
    },
    {
      id: 'v7',
      title: "நடுக்க நோய் உள்ளவர்களுக்கான உடற்பயிற்சி மற்றும் வாழ்க்கை முறை",
      titleTa: 'Parkinson’s Physiotherapy & Daily Care in Tamil',
      source: 'Tamil Health & Neuro Rehabilitation',
      language: 'ta',
      duration: '12:05',
      url: 'https://www.youtube.com/watch?v=5U78_t4RzP0',
      description:
        'பார்கின்சன் நோயாளிகளின் சமநிலையை மேம்படுத்தவும் தசை விரைப்பை குறைக்கவும் உதவும் உடற்பயிற்சிகள் மற்றும் குரல் வளப் பயிற்சிகள்.',
      topics: ['உடற்பயிற்சி', 'குரல் பயிற்சி', 'பராமரிப்பு'],
    },
  ];

  const articles: ArticleItem[] = [
    {
      title: 'Exploiting Nonlinear Recurrence and Fractal Scaling Properties for Voice Disorder Detection in Parkinson’s Disease',
      authors: 'Little, M. A., McSharry, P. E., Roberts, S. J., Costello, D. A. E., & Moroz, I. M.',
      journal: 'BioMedical Engineering OnLine, 6(1), 23',
      year: 2007,
      doi: '10.1186/1475-925X-6-23',
      url: 'https://doi.org/10.1186/1475-925X-6-23',
      takeaway:
        'Foundational paper behind the Oxford dataset. Proved that nonlinear dynamic features (RPDE, DFA, PPE) achieve >91% classification accuracy in distinguishing PD phonations from healthy controls.',
      tag: 'Acoustic Biomarkers',
    },
    {
      title: 'Accurate Telemonitoring of Parkinson’s Disease Progression by Noninvasive Speech Tests',
      authors: 'Tsanas, A., Little, M. A., McSharry, P. E., & Ramig, L. O.',
      journal: 'IEEE Transactions on Biomedical Engineering, 57(4), 884-893',
      year: 2010,
      doi: '10.1109/TBME.2009.2036000',
      url: 'https://doi.org/10.1109/TBME.2009.2036000',
      takeaway:
        'Demonstrated that remote telephone acoustic recordings can accurately predict motor and total UPDRS disability scores using automated speech signal processing algorithms.',
      tag: 'Telemonitoring',
    },
    {
      title: 'Parkinson Disease: State-of-the-Art Review',
      authors: 'Poewe, W., Seppi, K., Tanner, C. M., Halliday, G. M., Brundin, P., et al.',
      journal: 'Nature Reviews Disease Primers, 3, 17013',
      year: 2017,
      doi: '10.1038/nrdp.2017.13',
      url: 'https://doi.org/10.1038/nrdp.2017.13',
      takeaway:
        'Authoritative review of Parkinson epidemiology, cellular mechanisms (mitochondrial dysfunction, alpha-synuclein seeding), prodromal markers, and targeted therapeutic pipelines.',
      tag: 'Clinical Review',
    },
    {
      title: 'MDS Clinical Diagnostic Criteria for Parkinson’s Disease',
      authors: 'Postuma, R. B., Berg, D., Stern, M., Poewe, W., Olanow, C. W., et al.',
      journal: 'Movement Disorders, 30(12), 1591-1601',
      year: 2015,
      doi: '10.1002/mds.26424',
      url: 'https://doi.org/10.1002/mds.26424',
      takeaway:
        'The international gold-standard clinical diagnostic criteria established by the Movement Disorder Society, delineating motor requirements, red flags, and supportive criteria.',
      tag: 'Diagnostic Criteria',
    },
    {
      title: 'World Health Organization (WHO): Parkinson Disease Global Technical Brief',
      authors: 'World Health Organization Department of Mental Health and Substance Use',
      journal: 'WHO Technical Guidance Series',
      year: 2022,
      doi: 'ISBN 978-92-4-005098-3',
      url: 'https://www.who.int/news-room/fact-sheets/detail/parkinson-disease',
      takeaway:
        'Highlights that Parkinson is the fastest-growing neurological disorder globally, emphasizing non-invasive early screening, community rehabilitation, and multidisciplinary care.',
      tag: 'Global Health',
    },
  ];

  const filteredVideos = videos.filter((v) => {
    if (videoLang === 'all') return true;
    return v.language === videoLang;
  });

  return (
    <section className="py-20 border-t border-border bg-surface/30">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 space-y-12">
        {/* Section Header */}
        <div className="space-y-4 max-w-3xl">
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full border border-accent/20 bg-accent-subtle text-accent text-xs font-mono uppercase tracking-wider">
            <Brain className="w-3.5 h-3.5" />
            <span>Clinical Knowledge & Scientific Resources</span>
          </div>
          <h2 className="text-3xl sm:text-4xl font-extrabold tracking-tight text-txt">
            Understanding Parkinson's Disease (PD)
          </h2>
          <p className="text-sm sm:text-base text-txt-muted leading-relaxed">
            Parkinson's is a progressive neurodegenerative disorder originating from the selective degeneration of
            dopamine-producing neurons in the <em>substantia nigra</em>. Early acoustic dysphonia often manifests
            years prior to gross motor tremor, making voice a crucial non-invasive early screening biomarker.
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
                Loss of dopaminergic pathways in the basal ganglia disrupts the motor control circuit, causing
                diminished neuromuscular firing across respiratory and phonatory muscle groups.
              </p>
            </div>
            <div className="space-y-2">
              <span className="text-[10px] font-mono uppercase text-accent tracking-wider font-bold block">
                02 • Vocal Pathology
              </span>
              <h3 className="text-base font-bold text-txt">Hypokinetic Dysarthria</h3>
              <p className="text-xs text-txt-muted leading-relaxed">
                Laryngeal muscle rigidity impairs vocal cord adduction, creating involuntary micro-tremors (4–7 Hz),
                increased frequency perturbation (jitter), amplitude instability (shimmer), and lower HNR.
              </p>
            </div>
            <div className="space-y-2">
              <span className="text-[10px] font-mono uppercase text-accent tracking-wider font-bold block">
                03 • Research Triaging
              </span>
              <h3 className="text-base font-bold text-txt">Non-Invasive Screening</h3>
              <p className="text-xs text-txt-muted leading-relaxed">
                Acoustic analysis provides a rapid, cost-effective digital biomarker for longitudinal telemonitoring
                and clinical triaging, prior to confirmatory neurological examination.
              </p>
            </div>
          </div>
        </div>

        {/* Sub-Navigation Switcher */}
        <div className="flex flex-wrap items-center gap-2 border-b border-border pb-4">
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
            <div className="flex flex-wrap items-center justify-between gap-4">
              <div>
                <h3 className="text-lg font-bold text-txt">Motor vs. Non-Motor Symptom Spectrum</h3>
                <p className="text-xs text-txt-muted">
                  Parkinson's manifests through both conspicuous movement symptoms and systemic non-motor markers.
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
                  Motor (TRAP)
                </button>
                <button
                  onClick={() => setSymptomCategory('non-motor')}
                  className={`px-3 py-1 rounded-md font-semibold transition ${
                    symptomCategory === 'non-motor' ? 'bg-surface-2 text-txt' : 'text-txt-muted hover:text-txt'
                  }`}
                >
                  Non-Motor
                </button>
              </div>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5">
              {symptomsData.symptoms
                .filter((s) => symptomCategory === 'all' || s.type === symptomCategory)
                .map((sym) => (
                  <div
                    key={sym.id}
                    className={`card-nixtio p-5 space-y-2.5 border-border/80 transition ${
                      sym.type === 'motor' ? 'hover:border-accent/40' : 'hover:border-amber-500/40'
                    }`}
                  >
                    <div className="flex items-center justify-between gap-2">
                      <div className="flex items-center gap-1.5">
                        <span
                          className={`text-[10px] font-mono uppercase px-2 py-0.5 rounded border font-bold ${
                            sym.type === 'motor'
                              ? 'bg-accent-subtle text-accent border-accent/20'
                              : 'bg-amber-500/10 text-amber-400 border-amber-500/20'
                          }`}
                        >
                          {sym.type}
                        </span>
                        {sym.early_indicator && (
                          <span className="text-[9px] font-mono uppercase bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 px-1.5 py-0.5 rounded">
                            Early Sign
                          </span>
                        )}
                      </div>
                      <span className="text-[10px] font-mono text-txt-muted">Prev: {sym.prevalence}</span>
                    </div>
                    <h4 className="text-sm font-bold text-txt">{sym.name}</h4>
                    <p className="text-xs text-txt-muted leading-relaxed">{sym.description}</p>
                  </div>
                ))}
            </div>

            <div className="p-4 rounded-xl border border-border bg-surface-2/40 text-[11px] text-txt-muted flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3">
              <div>
                <strong>Clinical Sources:</strong> {symptomsData.sources.join(' • ')}
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
            <div>
              <h3 className="text-lg font-bold text-txt">Hoehn and Yahr Clinical Staging Scale</h3>
              <p className="text-xs text-txt-muted">
                The internationally recognized 5-stage scale describing progression from unilateral involvement to advanced disability.
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
                  className="card-nixtio p-5 flex flex-col justify-between space-y-4 border-border/80 hover:border-accent/40 transition group"
                >
                  <div className="space-y-3">
                    <div className="flex items-center justify-between gap-2">
                      <span
                        className={`text-[10px] font-mono uppercase px-2 py-0.5 rounded border font-bold ${
                          vid.language === 'ta'
                            ? 'bg-amber-500/10 text-amber-400 border-amber-500/20'
                            : 'bg-accent-subtle text-accent border-accent/20'
                        }`}
                      >
                        {vid.language === 'ta' ? 'தமிழ் (Tamil)' : 'English'}
                      </span>
                      <span className="text-[11px] font-mono text-txt-muted flex items-center gap-1">
                        <Clock className="w-3 h-3" /> {vid.duration}
                      </span>
                    </div>

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
                      className="touch-target px-3 py-1.5 rounded-lg bg-surface-2 hover:bg-accent hover:text-white text-txt text-xs font-semibold flex items-center gap-1.5 transition flex-shrink-0"
                    >
                      <Play className="w-3.5 h-3.5 fill-current" />
                      <span>Watch</span>
                    </a>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* SECTION 4: RESEARCH ARTICLES & LITERATURE */}
        {activeSection === 'articles' && (
          <div className="space-y-6 animate-fade-in">
            <div>
              <h3 className="text-lg font-bold text-txt">Foundational Scientific Literature</h3>
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
