import { useState, useEffect } from 'react';
import {
  Activity,
  AlertTriangle,
  Mic,
  Waves,
  Info,
  ArrowRight,
  RefreshCw,
  AlertCircle,
  FileCheck,
  ShieldCheck,
  Menu,
  X,
} from 'lucide-react';
import { apiClient, ScreeningResponse, ProblemDetail } from './api/client';
import { ThemeToggle } from './components/ThemeToggle';
import { LandingHero } from './components/LandingHero';
import { ProcessSteps } from './components/ProcessSteps';
import { VoiceTasksGrid } from './components/VoiceTasksGrid';
import { WhoItsFor } from './components/WhoItsFor';
import { FAQAccordion } from './components/FAQAccordion';
import { ConsentModal } from './components/ConsentModal';
import { AudioRecorder } from './components/AudioRecorder';
import { FileUpload } from './components/FileUpload';
import { ScreeningResult } from './components/ScreeningResult';
import { HistoryTable } from './components/HistoryTable';
import { ParkinsonKnowledgeHub } from './components/ParkinsonKnowledgeHub';

export default function App() {
  const [activeTab, setActiveTab] = useState<'overview' | 'screen' | 'history' | 'evidence'>('overview');
  const [inputMode, setInputMode] = useState<'record' | 'upload'>('record');
  const [patientId, setPatientId] = useState('');
  const [activeFile, setActiveFile] = useState<{ blob: Blob; filename: string } | null>(null);
  const [screeningResult, setScreeningResult] = useState<ScreeningResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [qualityRejection, setQualityRejection] = useState<any | null>(null);
  const [apiOnline, setApiOnline] = useState<boolean | null>(null);
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
  
  // Ethical consent state
  const [hasConsented, setHasConsented] = useState<boolean>(() => {
    return localStorage.getItem('steadyvox_consent') === 'true';
  });
  const [retainAudioConsent, setRetainAudioConsent] = useState<boolean>(true);
  const [showConsentModal, setShowConsentModal] = useState<boolean>(false);

  useEffect(() => {
    apiClient
      .checkHealth()
      .then(() => setApiOnline(true))
      .catch(() => setApiOnline(false));
  }, []);

  const handleStartScreeningClick = () => {
    if (!hasConsented) {
      setShowConsentModal(true);
    } else {
      setActiveTab('screen');
      window.scrollTo({ top: 0, behavior: 'smooth' });
    }
  };

  const handleConsentApproved = (retainAudio: boolean) => {
    setHasConsented(true);
    setRetainAudioConsent(retainAudio);
    localStorage.setItem('steadyvox_consent', 'true');
    setShowConsentModal(false);
    setActiveTab('screen');
    window.scrollTo({ top: 0, behavior: 'smooth' });
  };

  const handleAudioReady = (blob: Blob, filename: string) => {
    setActiveFile({ blob, filename });
    setError(null);
    setQualityRejection(null);
  };

  const handleAnalyze = async () => {
    if (!activeFile) {
      setError('Please provide an audio recording first.');
      return;
    }

    setLoading(true);
    setError(null);
    setQualityRejection(null);

    try {
      const response = await apiClient.screenAudio(
        activeFile.blob,
        activeFile.filename,
        patientId.trim() || undefined,
        retainAudioConsent
      );
      setScreeningResult(response);
      window.scrollTo({ top: 0, behavior: 'smooth' });
    } catch (err: any) {
      console.error(err);
      if (err.problemDetail) {
        const problem: ProblemDetail = err.problemDetail;
        setError(problem.detail);
        if (problem.quality_report) {
          setQualityRejection(problem.quality_report);
        }
      } else {
        setError(err.message || 'Screening analysis failed. Please verify microphone signal.');
      }
    } finally {
      setLoading(false);
    }
  };

  const handleReset = () => {
    setScreeningResult(null);
    setActiveFile(null);
    setError(null);
    setQualityRejection(null);
  };

  return (
    <div className="min-h-screen flex flex-col bg-bg text-txt">
      {/* Consent Modal Dialog */}
      <ConsentModal
        isOpen={showConsentModal}
        onConsent={handleConsentApproved}
        onCancel={() => setShowConsentModal(false)}
      />

      {/* Mandatory Top Regulatory Disclaimer Alert */}
      <div className="bg-amber-500 text-slate-950 px-4 py-2 text-xs font-bold flex items-center justify-center gap-2 border-b border-amber-600 shadow-sm text-center">
        <AlertTriangle className="w-4 h-4 flex-shrink-0 text-slate-950" />
        <span>
          RESEARCH SCREENING TOOL ONLY — NOT A MEDICAL DIAGNOSIS. For investigational, scientific, and educational use only.
        </span>
      </div>

      {/* Sticky Translucent Nixtio Header Nav */}
      <header className="sticky top-0 z-40 bg-bg/80 backdrop-blur-xl border-b border-border transition-colors">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-18 flex items-center justify-between">
          {/* Logo & Brand */}
          <div
            onClick={() => setActiveTab('overview')}
            className="flex items-center gap-3 cursor-pointer group"
          >
            <div className="w-10 h-10 rounded-xl bg-accent text-white flex items-center justify-center shadow-lg shadow-accent/20 group-hover:scale-105 transition">
              <Activity className="w-5 h-5" />
            </div>
            <div>
              <div className="flex items-center gap-2">
                <span className="font-extrabold text-lg tracking-tight text-txt">SteadyVox</span>
                <span className="text-[10px] font-mono uppercase bg-accent-subtle text-accent px-2 py-0.5 rounded border border-accent/20">
                  v2.1
                </span>
              </div>
              <p className="text-[11px] text-txt-muted hidden sm:block">
                Voice Biomarkers for Parkinson's Disease Screening
              </p>
            </div>
          </div>

          {/* Desktop Nav Links */}
          <nav className="hidden md:flex items-center gap-1 border border-border bg-surface/60 p-1 rounded-full">
            <button
              onClick={() => setActiveTab('overview')}
              className={`touch-target px-4 py-1.5 rounded-full text-xs font-semibold transition ${
                activeTab === 'overview' ? 'bg-surface-2 text-txt border border-border shadow-sm' : 'text-txt-muted hover:text-txt'
              }`}
            >
              Overview
            </button>
            <button
              onClick={() => setActiveTab('screen')}
              className={`touch-target px-4 py-1.5 rounded-full text-xs font-semibold transition ${
                activeTab === 'screen' ? 'bg-surface-2 text-txt border border-border shadow-sm' : 'text-txt-muted hover:text-txt'
              }`}
            >
              Voice Screening
            </button>
            <button
              onClick={() => setActiveTab('history')}
              className={`touch-target px-4 py-1.5 rounded-full text-xs font-semibold transition ${
                activeTab === 'history' ? 'bg-surface-2 text-txt border border-border shadow-sm' : 'text-txt-muted hover:text-txt'
              }`}
            >
              Audit History
            </button>
            <button
              onClick={() => setActiveTab('evidence')}
              className={`touch-target px-4 py-1.5 rounded-full text-xs font-semibold transition ${
                activeTab === 'evidence' ? 'bg-surface-2 text-txt border border-border shadow-sm' : 'text-txt-muted hover:text-txt'
              }`}
            >
              Clinical Evidence
            </button>
          </nav>

          {/* Header Action Controls */}
          <div className="flex items-center gap-3">
            {/* API Status Badge */}
            <div className="hidden lg:flex items-center gap-1.5 px-3 py-1.5 rounded-full border border-border bg-surface text-[11px] font-mono text-txt-muted">
              <span
                className={`w-2 h-2 rounded-full ${
                  apiOnline === true ? 'bg-emerald-400 animate-pulse' : 'bg-red-400'
                }`}
              />
              <span>{apiOnline ? 'API Operational' : 'API Standby'}</span>
            </div>

            {/* Dark/Light Mode Switcher */}
            <ThemeToggle />

            {/* High-contrast Primary CTA */}
            <button
              type="button"
              onClick={handleStartScreeningClick}
              className="hidden sm:flex touch-target px-5 py-2.5 bg-txt text-bg hover:opacity-90 text-xs font-bold rounded-full transition shadow-md items-center gap-1.5"
            >
              <span>Start Voice Test</span>
              <ArrowRight className="w-3.5 h-3.5" />
            </button>

            {/* Mobile Hamburger */}
            <button
              type="button"
              onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
              className="md:hidden touch-target p-2 text-txt-muted hover:text-txt rounded-lg"
              aria-label="Toggle navigation menu"
            >
              {mobileMenuOpen ? <X className="w-6 h-6" /> : <Menu className="w-6 h-6" />}
            </button>
          </div>
        </div>

        {/* Mobile Dropdown Menu */}
        {mobileMenuOpen && (
          <div className="md:hidden border-b border-border bg-surface p-4 space-y-2 animate-fade-in">
            <button
              onClick={() => {
                setActiveTab('overview');
                setMobileMenuOpen(false);
              }}
              className="w-full text-left px-4 py-2.5 rounded-xl text-xs font-semibold text-txt hover:bg-surface-2"
            >
              Overview
            </button>
            <button
              onClick={() => {
                setActiveTab('screen');
                setMobileMenuOpen(false);
              }}
              className="w-full text-left px-4 py-2.5 rounded-xl text-xs font-semibold text-txt hover:bg-surface-2"
            >
              Voice Screening
            </button>
            <button
              onClick={() => {
                setActiveTab('history');
                setMobileMenuOpen(false);
              }}
              className="w-full text-left px-4 py-2.5 rounded-xl text-xs font-semibold text-txt hover:bg-surface-2"
            >
              Audit History
            </button>
            <button
              onClick={() => {
                setActiveTab('evidence');
                setMobileMenuOpen(false);
              }}
              className="w-full text-left px-4 py-2.5 rounded-xl text-xs font-semibold text-txt hover:bg-surface-2"
            >
              Clinical Evidence
            </button>
            <div className="pt-2">
              <button
                type="button"
                onClick={() => {
                  setMobileMenuOpen(false);
                  handleStartScreeningClick();
                }}
                className="w-full touch-target px-5 py-3 bg-accent text-white text-xs font-bold rounded-xl"
              >
                Start Voice Test
              </button>
            </div>
          </div>
        )}
      </header>

      {/* Main Content Sections */}
      <main className="flex-1 w-full">
        {activeTab === 'overview' && (
          <div className="space-y-0">
            <LandingHero
              onStartTest={handleStartScreeningClick}
              onViewEvidence={() => setActiveTab('evidence')}
            />
            <ProcessSteps />
            <ParkinsonKnowledgeHub />
            <VoiceTasksGrid />
            <WhoItsFor />
            <FAQAccordion />
          </div>
        )}

        {activeTab === 'screen' && (
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-10 w-full space-y-8 animate-fade-in">
            {screeningResult ? (
              <ScreeningResult result={screeningResult} onReset={handleReset} />
            ) : (
              <div className="space-y-8">
                {/* Screening Setup Banner */}
                <div className="card-nixtio p-6 sm:p-8 flex flex-col md:flex-row items-start md:items-center justify-between gap-6">
                  <div className="space-y-1.5">
                    <div className="flex items-center gap-2 text-xs font-bold uppercase text-accent tracking-wider font-mono">
                      <Waves className="w-4 h-4" />
                      Phonatory Dysarthria Assessment
                    </div>
                    <h2 className="text-2xl sm:text-3xl font-extrabold tracking-tight text-txt">
                      Parkinson's Disease Voice Screening
                    </h2>
                    <p className="text-xs sm:text-sm text-txt-muted max-w-2xl leading-relaxed">
                      Sustain vowel <strong className="text-txt">/a/</strong> for 3–5 seconds. SteadyVox extracts 22 gold-standard acoustic features and scores them via our clinical Oxford-validated Tabular MLP.
                    </p>
                  </div>
                  <div className="flex-shrink-0 flex items-center gap-2.5 px-4 py-3 rounded-xl border border-border bg-surface-2 text-xs text-txt-muted">
                    <ShieldCheck className="w-5 h-5 text-accent flex-shrink-0" />
                    <div>
                      <span className="font-bold text-txt block">Quality-Gated</span>
                      <span className="text-[11px]">Real-time noise & clipping checks</span>
                    </div>
                  </div>
                </div>

                {/* Screening Input Panel */}
                <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
                  <div className="lg:col-span-2 card-nixtio p-6 sm:p-8 space-y-6">
                    {/* Participant ID Input */}
                    <div>
                      <label className="block text-xs font-bold uppercase tracking-wider text-txt-muted mb-2 font-mono">
                        Participant / Session Identifier (Optional)
                      </label>
                      <input
                        type="text"
                        placeholder="e.g. PARTICIPANT-042 or TRIAL-B-01"
                        value={patientId}
                        onChange={(e) => setPatientId(e.target.value)}
                        className="w-full px-4 py-3 text-xs border border-border rounded-xl bg-surface-2 text-txt focus:outline-none focus:border-accent transition font-mono"
                      />
                    </div>

                    {/* Mode Toggle: Record vs Upload */}
                    <div className="flex items-center gap-3 border-b border-border pb-5">
                      <button
                        type="button"
                        onClick={() => {
                          setInputMode('record');
                          setActiveFile(null);
                        }}
                        className={`touch-target px-4 py-2 rounded-xl text-xs font-bold flex items-center gap-2 transition ${
                          inputMode === 'record'
                            ? 'bg-accent text-white shadow-md'
                            : 'bg-surface-2 text-txt-muted hover:text-txt'
                        }`}
                      >
                        <Mic className="w-4 h-4" /> Live Microphone Recording
                      </button>
                      <button
                        type="button"
                        onClick={() => {
                          setInputMode('upload');
                          setActiveFile(null);
                        }}
                        className={`touch-target px-4 py-2 rounded-xl text-xs font-bold flex items-center gap-2 transition ${
                          inputMode === 'upload'
                            ? 'bg-accent text-white shadow-md'
                            : 'bg-surface-2 text-txt-muted hover:text-txt'
                        }`}
                      >
                        <Waves className="w-4 h-4" /> Upload Audio File (.wav/.mp3)
                      </button>
                    </div>

                    {/* Active Input Component */}
                    {inputMode === 'record' ? (
                      <AudioRecorder onAudioReady={handleAudioReady} disabled={loading} />
                    ) : (
                      <FileUpload onFileSelected={(file) => handleAudioReady(file, file.name)} disabled={loading} />
                    )}

                    {/* Quality Rejection Feedback Box */}
                    {qualityRejection && (
                      <div className="p-5 rounded-xl border border-red-500/30 bg-red-500/10 text-xs text-red-300 space-y-2 animate-fade-in">
                        <div className="flex items-center gap-2 font-bold text-red-400">
                          <AlertCircle className="w-4 h-4 flex-shrink-0" />
                          <span>Audio Failed Acoustic Quality Gate:</span>
                        </div>
                        <ul className="list-disc list-inside space-y-1 text-[11px] pl-1 text-red-300/90">
                          {qualityRejection.rejection_reasons?.map((r: string, rIdx: number) => (
                            <li key={rIdx}>{r}</li>
                          ))}
                        </ul>
                        {qualityRejection.recommendations?.length > 0 && (
                          <div className="pt-1 text-[11px] text-txt">
                            <strong>Recommendation:</strong> {qualityRejection.recommendations.join(' ')}
                          </div>
                        )}
                      </div>
                    )}

                    {/* Generic Error Box */}
                    {error && !qualityRejection && (
                      <div className="p-4 rounded-xl border border-red-500/30 bg-red-500/10 text-xs text-red-400 flex items-center gap-2.5">
                        <AlertCircle className="w-4 h-4 flex-shrink-0" />
                        <span>{error}</span>
                      </div>
                    )}

                    {/* Action Execution Strip */}
                    <div className="pt-4 flex flex-col sm:flex-row items-center justify-between gap-4 border-t border-border">
                      <span className="text-xs text-txt-muted">
                        {activeFile ? (
                          <span className="text-emerald-400 flex items-center gap-1.5 font-medium">
                            <FileCheck className="w-4 h-4" /> Ready for Analysis ({activeFile.filename})
                          </span>
                        ) : (
                          'Provide a 3–5 second sustained vowel sample to proceed.'
                        )}
                      </span>
                      <button
                        type="button"
                        onClick={handleAnalyze}
                        disabled={!activeFile || loading}
                        className="w-full sm:w-auto touch-target px-8 py-3.5 bg-accent hover:bg-accent-hover disabled:opacity-40 disabled:cursor-not-allowed text-white text-xs font-bold rounded-xl shadow-lg transition flex items-center justify-center gap-2"
                      >
                        {loading ? (
                          <>
                            <RefreshCw className="w-4 h-4 animate-spin" /> Processing DSP & Dual-Path Inference...
                          </>
                        ) : (
                          <>
                            Run Screening Analysis <ArrowRight className="w-4 h-4" />
                          </>
                        )}
                      </button>
                    </div>
                  </div>

                  {/* Sidebar Protocol Guidance */}
                  <div className="space-y-6">
                    <div className="card-nixtio p-6 space-y-4">
                      <h3 className="font-bold text-txt text-sm flex items-center gap-2">
                        <Info className="w-4 h-4 text-accent" /> Phonation Protocol
                      </h3>
                      <ol className="text-xs text-txt-muted space-y-3 list-decimal list-inside leading-relaxed">
                        <li>Sit upright in a quiet room with minimal ambient noise.</li>
                        <li>Take a normal breath and produce a continuous, sustained vowel <strong className="text-txt">"aaah"</strong>.</li>
                        <li>Maintain a steady, comfortable pitch and volume for at least <strong className="text-txt">3 to 5 seconds</strong>.</li>
                        <li>Avoid coughing, pitch glides, or sudden volume shifts during phonation.</li>
                      </ol>
                    </div>

                    <div className="card-nixtio p-6 space-y-3">
                      <h4 className="font-bold text-xs uppercase tracking-wider text-txt-muted font-mono">
                        Biomarkers Evaluated
                      </h4>
                      <div className="space-y-2.5 text-xs text-txt-muted">
                        <div className="p-3 rounded-lg border border-border bg-surface-2/60">
                          <strong className="text-txt block mb-0.5">Frequency Instability (Jitter)</strong>
                          <span>Cycle-to-cycle perturbation caused by laryngeal rigidity.</span>
                        </div>
                        <div className="p-3 rounded-lg border border-border bg-surface-2/60">
                          <strong className="text-txt block mb-0.5">Amplitude Variance (Shimmer)</strong>
                          <span>Cycle amplitude variance from incomplete vocal fold adduction.</span>
                        </div>
                        <div className="p-3 rounded-lg border border-border bg-surface-2/60">
                          <strong className="text-txt block mb-0.5">Harmonics-to-Noise Ratio (HNR)</strong>
                          <span>Quantifies glottal turbulence and breathiness.</span>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            )}
          </div>
        )}

        {activeTab === 'history' && (
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-10 w-full animate-fade-in">
            <HistoryTable />
          </div>
        )}

        {activeTab === 'evidence' && (
          <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-12 space-y-8 text-sm text-txt-muted leading-relaxed animate-fade-in">
            <div>
              <span className="eyebrow block">Scientific & Algorithmic Documentation</span>
              <h1 className="text-3xl sm:text-4xl font-extrabold text-txt tracking-tight mt-1">
                Clinical Evidence & Validation
              </h1>
              <p className="text-xs text-txt-muted mt-1 font-mono">
                SteadyVox Dual-Path Architecture & Model Card Specification
              </p>
            </div>

            {/* Non-diagnostic Alert */}
            <div className="p-4 rounded-xl border border-amber-500/30 bg-amber-500/10 text-amber-400 text-xs leading-relaxed space-y-1">
              <strong className="block font-bold uppercase tracking-wider text-amber-300">
                Research Screening Tool Only — Not a Medical Diagnosis
              </strong>
              <p className="text-amber-300/80">
                SteadyVox is designed exclusively for observational studies, clinical triaging, and biomedical research. Under no circumstances should results be interpreted as medical diagnosis, treatment advice, or prognosis.
              </p>
            </div>

            <div className="card-nixtio p-6 sm:p-8 space-y-4">
              <h2 className="text-lg font-bold text-txt">Primary Model: Tabular MLP</h2>
              <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 text-xs font-mono py-2">
                <div className="p-3 rounded-lg border border-border bg-surface-2">
                  <span className="text-[10px] uppercase text-txt-muted block">Dataset</span>
                  <strong className="text-txt">Oxford UCI</strong>
                </div>
                <div className="p-3 rounded-lg border border-border bg-surface-2">
                  <span className="text-[10px] uppercase text-txt-muted block">ROC-AUC</span>
                  <strong className="text-emerald-400">0.8925</strong>
                </div>
                <div className="p-3 rounded-lg border border-border bg-surface-2">
                  <span className="text-[10px] uppercase text-txt-muted block">F1-Score</span>
                  <strong className="text-emerald-400">0.9394</strong>
                </div>
                <div className="p-3 rounded-lg border border-border bg-surface-2">
                  <span className="text-[10px] uppercase text-txt-muted block">Sensitivity</span>
                  <strong className="text-emerald-400">100.0%</strong>
                </div>
              </div>
              <p className="text-xs text-txt-muted">
                Trained on real phonations from 31 individuals (23 with Parkinson's, 8 healthy controls) from the University of Oxford. Evaluated via 5-fold stratified cross-validation with feature scaling calibrated against real acoustic distributions.
              </p>
            </div>

            <div className="card-nixtio p-6 sm:p-8 space-y-4">
              <h2 className="text-lg font-bold text-txt">Secondary Model: CNN + BiLSTM</h2>
              <p className="text-xs text-txt-muted">
                Processes 128-band Log Mel-Spectrograms through a 4-stage 2D Convolutional neural network followed by a Bidirectional LSTM. Evaluated on a 600-speaker biophysical sustained vowel simulation benchmark to capture time-frequency tremor dynamics. Synthetic metrics are transparently flagged as an ablation benchmark.
              </p>
            </div>

            <div className="card-nixtio p-6 sm:p-8 space-y-4">
              <h3 className="text-base font-bold text-txt">Primary Scientific Citations</h3>
              <ul className="text-xs text-txt-muted space-y-2.5 list-disc list-inside">
                <li>
                  <strong className="text-txt">Little, M. A., et al. (2009).</strong> <em>Suitability of dysphonia measurements for telemonitoring of Parkinson's disease.</em> IEEE Transactions on Biomedical Engineering, 56(4), 1015-1022.
                </li>
                <li>
                  <strong className="text-txt">Rusz, J., et al. (2011).</strong> <em>Quantitative acoustic measurements for characterization of speech and voice disorders in untreated early Parkinson's disease.</em> JASA, 129(1), 350-367.
                </li>
                <li>
                  <strong className="text-txt">Boersma, P., & Weenink, D. (2021).</strong> <em>Praat: doing phonetics by computer.</em> Computer program.
                </li>
              </ul>
            </div>
          </div>
        )}
      </main>

      {/* Minimal Nixtio Footer */}
      <footer className="border-t border-border bg-surface py-10 mt-auto">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 flex flex-col md:flex-row items-center justify-between gap-6 text-xs text-txt-muted">
          <div className="space-y-1 text-center md:text-left">
            <div className="flex items-center justify-center md:justify-start gap-2">
              <span className="font-bold text-txt">SteadyVox</span>
              <span>— Vocal Biomarker Screening</span>
            </div>
            <p className="text-[11px] text-txt-muted">
              Built with FastAPI, PyTorch & React. Codebase on GitHub.
            </p>
          </div>

          <div className="p-2.5 px-4 rounded-xl border border-amber-500/30 bg-amber-500/10 text-amber-400 text-xs flex items-center gap-2 text-center">
            <AlertTriangle className="w-4 h-4 flex-shrink-0" />
            <span>Research screening tool only — not a clinical diagnosis.</span>
          </div>
        </div>
      </footer>
    </div>
  );
}
