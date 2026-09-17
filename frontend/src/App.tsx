import { useState, useEffect } from 'react';
import {
  Activity,
  AlertTriangle,
  Mic,
  ShieldAlert,
  Waves,
  Info,
  ArrowRight,
  RefreshCw,
  AlertCircle,
  FileCheck,
} from 'lucide-react';
import { apiClient, ScreeningResponse } from './api/client';
import { AudioRecorder } from './components/AudioRecorder';
import { FileUpload } from './components/FileUpload';
import { ScreeningResult } from './components/ScreeningResult';
import { HistoryTable } from './components/HistoryTable';

export default function App() {
  const [activeTab, setActiveTab] = useState<'screen' | 'history' | 'about'>('screen');
  const [inputMode, setInputMode] = useState<'record' | 'upload'>('record');
  const [patientId, setPatientId] = useState('');
  const [activeFile, setActiveFile] = useState<{ blob: Blob; filename: string } | null>(null);
  const [screeningResult, setScreeningResult] = useState<ScreeningResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [apiOnline, setApiOnline] = useState<boolean | null>(null);

  useEffect(() => {
    apiClient
      .checkHealth()
      .then(() => setApiOnline(true))
      .catch(() => setApiOnline(false));
  }, []);

  const handleAudioReady = (blob: Blob, filename: string) => {
    setActiveFile({ blob, filename });
    setError(null);
  };

  const handleAnalyze = async () => {
    if (!activeFile) {
      setError('Please record or upload an audio sample first.');
      return;
    }

    setLoading(true);
    setError(null);

    try {
      const response = await apiClient.screenAudio(
        activeFile.blob,
        activeFile.filename,
        patientId.trim() || undefined
      );
      setScreeningResult(response);
    } catch (err: any) {
      console.error(err);
      setError(err.message || 'Screening analysis failed. Please verify audio input.');
    } finally {
      setLoading(false);
    }
  };

  const handleReset = () => {
    setScreeningResult(null);
    setActiveFile(null);
    setError(null);
  };

  return (
    <div className="min-h-screen flex flex-col bg-slate-50 text-slate-800">
      {/* Mandatory Top Regulatory & Medical Disclaimer Alert */}
      <div className="bg-amber-500 text-slate-950 px-4 py-2 text-xs md:text-sm font-bold flex items-center justify-center gap-2 shadow-sm border-b border-amber-600">
        <AlertTriangle className="w-4 h-4 flex-shrink-0 text-slate-950" />
        <span>
          RESEARCH SCREENING TOOL ONLY — NOT A MEDICAL DIAGNOSIS. For investigational, scientific, and educational use only.
        </span>
      </div>

      {/* Main Navbar */}
      <header className="bg-white border-b border-slate-200 sticky top-0 z-30">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-xl bg-teal-600 text-white flex items-center justify-center shadow-sm">
              <Activity className="w-6 h-6" />
            </div>
            <div>
              <div className="flex items-center gap-2">
                <span className="font-bold text-lg text-slate-900 tracking-tight">SteadyVox</span>
                <span className="text-[10px] font-mono uppercase bg-teal-50 text-teal-700 px-2 py-0.5 rounded border border-teal-200">
                  CNN + BiLSTM Research
                </span>
              </div>
              <p className="text-xs text-slate-500 hidden sm:block">
                Deep Neural Voice Analysis for Parkinson's Disease Acoustic Biomarkers
              </p>
            </div>
          </div>

          <div className="flex items-center gap-3">
            <div className="flex items-center gap-1.5 px-3 py-1 bg-slate-100 rounded-full text-xs font-medium text-slate-600">
              <div
                className={`w-2 h-2 rounded-full ${
                  apiOnline === true
                    ? 'bg-emerald-500 animate-pulse'
                    : apiOnline === false
                    ? 'bg-red-500'
                    : 'bg-amber-400'
                }`}
              />
              <span>{apiOnline ? 'API Connected' : 'API Standby'}</span>
            </div>

            <nav className="flex items-center bg-slate-100 p-1 rounded-lg">
              <button
                onClick={() => setActiveTab('screen')}
                className={`px-3 py-1.5 rounded-md text-xs font-medium transition ${
                  activeTab === 'screen' ? 'bg-white text-teal-700 shadow-sm' : 'text-slate-600 hover:text-slate-900'
                }`}
              >
                Screening
              </button>
              <button
                onClick={() => setActiveTab('history')}
                className={`px-3 py-1.5 rounded-md text-xs font-medium transition ${
                  activeTab === 'history' ? 'bg-white text-teal-700 shadow-sm' : 'text-slate-600 hover:text-slate-900'
                }`}
              >
                History
              </button>
              <button
                onClick={() => setActiveTab('about')}
                className={`px-3 py-1.5 rounded-md text-xs font-medium transition ${
                  activeTab === 'about' ? 'bg-white text-teal-700 shadow-sm' : 'text-slate-600 hover:text-slate-900'
                }`}
              >
                About
              </button>
            </nav>
          </div>
        </div>
      </header>

      {/* Main Container */}
      <main className="flex-1 max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 w-full">
        {activeTab === 'screen' && (
          <div className="space-y-6">
            {screeningResult ? (
              <ScreeningResult result={screeningResult} onReset={handleReset} />
            ) : (
              <div className="space-y-6">
                {/* Introduction Banner */}
                <div className="bg-white rounded-2xl border border-slate-200 p-6 sm:p-8 shadow-sm flex flex-col md:flex-row items-start md:items-center justify-between gap-6">
                  <div className="space-y-1.5">
                    <div className="flex items-center gap-2 text-xs font-semibold uppercase text-teal-700">
                      <Waves className="w-4 h-4" />
                      Acoustic Dysarthria Screening
                    </div>
                    <h1 className="text-xl sm:text-2xl font-bold text-slate-900 tracking-tight">
                      Parkinson's Disease Voice Biomarker Screening
                    </h1>
                    <p className="text-xs sm:text-sm text-slate-600 max-w-2xl leading-relaxed">
                      Evaluates vocal tremor (4–7 Hz), frequency perturbation (Jitter), amplitude perturbation (Shimmer),
                      and glottal noise (HNR) from sustained vowel phonations (/a/ or /o/) using CNN + BiLSTM deep neural networks.
                    </p>
                  </div>
                  <div className="flex-shrink-0 flex items-center gap-2 bg-slate-50 border border-slate-200 px-4 py-3 rounded-xl text-xs text-slate-700">
                    <ShieldAlert className="w-5 h-5 text-amber-500 flex-shrink-0" />
                    <div>
                      <span className="font-semibold block">Non-Diagnostic Tool</span>
                      <span className="text-[11px] text-slate-500">Research & triage only</span>
                    </div>
                  </div>
                </div>

                {/* Screening Setup & Input Box */}
                <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                  <div className="lg:col-span-2 bg-white rounded-2xl border border-slate-200 p-6 sm:p-8 shadow-sm space-y-6">
                    {/* Patient / Session Tag Input */}
                    <div>
                      <label className="block text-xs font-semibold text-slate-700 mb-1">
                        Participant / Session Identifier (Optional)
                      </label>
                      <input
                        type="text"
                        placeholder="e.g. PATIENT-042 or TRIAL-B-01"
                        value={patientId}
                        onChange={(e) => setPatientId(e.target.value)}
                        className="w-full px-3.5 py-2 text-xs border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-teal-500 focus:border-transparent"
                      />
                    </div>

                    {/* Mode Toggle: Record vs Upload */}
                    <div className="flex items-center gap-3 border-b border-slate-100 pb-4">
                      <button
                        type="button"
                        onClick={() => {
                          setInputMode('record');
                          setActiveFile(null);
                        }}
                        className={`px-4 py-2 rounded-lg text-xs font-semibold flex items-center gap-2 transition ${
                          inputMode === 'record'
                            ? 'bg-teal-600 text-white shadow-sm'
                            : 'bg-slate-100 text-slate-600 hover:bg-slate-200'
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
                        className={`px-4 py-2 rounded-lg text-xs font-semibold flex items-center gap-2 transition ${
                          inputMode === 'upload'
                            ? 'bg-teal-600 text-white shadow-sm'
                            : 'bg-slate-100 text-slate-600 hover:bg-slate-200'
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

                    {/* Error Display */}
                    {error && (
                      <div className="p-4 bg-red-50 text-red-700 text-xs rounded-xl border border-red-200 flex items-center gap-2">
                        <AlertCircle className="w-4 h-4 flex-shrink-0" />
                        <span>{error}</span>
                      </div>
                    )}

                    {/* Action Trigger */}
                    <div className="pt-2 flex items-center justify-between">
                      <span className="text-[11px] text-slate-400">
                        {activeFile ? (
                          <span className="text-emerald-700 flex items-center gap-1 font-medium">
                            <FileCheck className="w-3.5 h-3.5" /> Phonation sample ready ({activeFile.filename})
                          </span>
                        ) : (
                          'Provide a sustained vowel sample to proceed.'
                        )}
                      </span>
                      <button
                        type="button"
                        onClick={handleAnalyze}
                        disabled={!activeFile || loading}
                        className="px-6 py-3 bg-teal-600 hover:bg-teal-700 disabled:opacity-50 disabled:cursor-not-allowed text-white text-xs font-bold rounded-xl shadow-sm flex items-center gap-2 transition"
                      >
                        {loading ? (
                          <>
                            <RefreshCw className="w-4 h-4 animate-spin" /> Analyzing Acoustic Signals...
                          </>
                        ) : (
                          <>
                            Run Screening Analysis <ArrowRight className="w-4 h-4" />
                          </>
                        )}
                      </button>
                    </div>
                  </div>

                  {/* Protocol & Science Guidance Sidebar */}
                  <div className="space-y-4">
                    <div className="bg-white rounded-2xl border border-slate-200 p-6 shadow-sm space-y-4">
                      <h3 className="font-bold text-slate-900 text-sm flex items-center gap-2">
                        <Info className="w-4 h-4 text-teal-600" /> Phonation Protocol
                      </h3>
                      <ol className="text-xs text-slate-600 space-y-2.5 list-decimal list-inside leading-relaxed">
                        <li>Sit upright in a quiet room with minimal background noise.</li>
                        <li>Take a normal breath and produce a continuous, sustained vowel <strong>"aaah"</strong> (as in <em>father</em>).</li>
                        <li>Maintain a steady comfortable pitch and volume for at least <strong>3 to 5 seconds</strong>.</li>
                        <li>Avoid coughing, swallowing, or sudden pitch shifts during phonation.</li>
                      </ol>
                    </div>

                    <div className="bg-white rounded-2xl border border-slate-200 p-6 shadow-sm space-y-3">
                      <h4 className="font-semibold text-slate-800 text-xs uppercase tracking-wide">
                        What SteadyVox Evaluates
                      </h4>
                      <div className="space-y-2 text-xs text-slate-600">
                        <div className="p-2.5 rounded-lg bg-slate-50 border border-slate-100">
                          <strong className="text-slate-800 block">Spectral Micro-Tremor</strong>
                          <span>4–7 Hz frequency oscillations detected by the CNN+BiLSTM architecture.</span>
                        </div>
                        <div className="p-2.5 rounded-lg bg-slate-50 border border-slate-100">
                          <strong className="text-slate-800 block">Jitter & Shimmer Perturbations</strong>
                          <span>Cycle-to-cycle frequency and amplitude instability.</span>
                        </div>
                        <div className="p-2.5 rounded-lg bg-slate-50 border border-slate-100">
                          <strong className="text-slate-800 block">Harmonics-to-Noise Ratio (HNR)</strong>
                          <span>Quantifies breathiness and glottal turbulence.</span>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            )}
          </div>
        )}

        {activeTab === 'history' && <HistoryTable />}

        {activeTab === 'about' && (
          <div className="bg-white rounded-2xl border border-slate-200 p-8 sm:p-10 max-w-3xl mx-auto space-y-6 text-sm text-slate-600 leading-relaxed shadow-sm">
            <div>
              <span className="text-xs font-mono uppercase bg-teal-50 text-teal-700 px-2.5 py-1 rounded border border-teal-200">
                Scientific Documentation
              </span>
              <h2 className="text-2xl font-bold text-slate-900 mt-2">About SteadyVox Voice Analysis</h2>
              <p className="text-xs text-slate-500 mt-1">
                Investigational Deep Learning Screening Platform for Parkinsonian Dysarthria
              </p>
            </div>

            <div className="p-4 bg-amber-50 border-l-4 border-amber-500 rounded-r-xl text-amber-900 text-xs leading-relaxed space-y-1">
              <strong className="block font-bold uppercase text-amber-950">
                Research Screening Tool Only — Not a Medical Diagnosis
              </strong>
              <p>
                SteadyVox is designed exclusively for clinical research, observational studies, and screening triaging.
                Under no circumstances should the results provided by this system be construed as medical diagnosis,
                treatment advice, or prognosis. Always consult a qualified neurologist or physician for neurological evaluations.
              </p>
            </div>

            <div className="space-y-3">
              <h3 className="text-base font-bold text-slate-800">Biophysical Rationale</h3>
              <p>
                Parkinson's Disease (PD) is characterized by neurodegeneration in the substantia nigra, leading to hypokinetic
                dysarthria. Early clinical manifestations frequently include vocal fold bowing, laryngeal muscle rigidity, and
                tremor, which impact phonation stability well before gross motor symptoms emerge.
              </p>
              <p>
                SteadyVox pairs clinical gold-standard acoustic algorithms (Praat/Parselmouth) with time-preserving Convolutional
                Neural Networks and Bidirectional Long Short-Term Memory (CNN + BiLSTM) networks to capture both spectral
                abnormalities and temporal tremor dynamics.
              </p>
            </div>

            <div className="space-y-3">
              <h3 className="text-base font-bold text-slate-800">Scientific References</h3>
              <ul className="text-xs text-slate-500 space-y-1.5 list-disc list-inside">
                <li>
                  Little, M. A., et al. (2009). <em>Suitability of dysphonia measurements for telemonitoring of Parkinson's disease</em>. IEEE Transactions on Biomedical Engineering.
                </li>
                <li>
                  Boersma, P., & Weenink, D. (2021). <em>Praat: doing phonetics by computer</em>.
                </li>
                <li>
                  Rusz, J., et al. (2011). <em>Quantitative acoustic measurements for characterization of speech and voice disorders in early untreated Parkinson's disease</em>. The Journal of the Acoustical Society of America.
                </li>
              </ul>
            </div>
          </div>
        )}
      </main>

      {/* Persistent Legal Disclaimer Footer */}
      <footer className="bg-white border-t border-slate-200 py-6 mt-auto">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 flex flex-col md:flex-row items-center justify-between gap-4 text-xs text-slate-500">
          <div>
            © {new Date().getFullYear()} SteadyVox Research Group. Built with PyTorch, FastAPI & React.
          </div>
          <div className="text-center md:text-right font-medium text-amber-900 bg-amber-50 px-3.5 py-1.5 rounded-lg border border-amber-200 flex items-center gap-1.5">
            <AlertTriangle className="w-3.5 h-3.5 text-amber-600" />
            <span>Research screening tool only — not a medical diagnosis.</span>
          </div>
        </div>
      </footer>
    </div>
  );
}
