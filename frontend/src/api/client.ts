/**
 * SteadyVox Typed API Client.
 * 
 * RESEARCH SCREENING TOOL ONLY — NOT A MEDICAL DIAGNOSIS.
 */

export interface Biomarkers {
  f0_mean: number;
  f0_std: number;
  f0_min: number;
  f0_max: number;
  jitter_local_percent: number;
  jitter_rap_percent: number;
  jitter_ppq5_percent: number;
  shimmer_local_percent: number;
  shimmer_local_db: number;
  shimmer_apq3_percent: number;
  shimmer_apq5_percent: number;
  hnr_mean_db: number;
  rpde?: number;
  dfa?: number;
  ppe?: number;
}

export interface QualityReport {
  is_acceptable: boolean;
  duration_seconds: number;
  snr_db: number;
  clipping_ratio: number;
  silence_ratio: number;
  peak_amplitude: number;
  rejection_reasons: string[];
  recommendations: string[];
}

export interface ModelProvenance {
  name: string;
  version: string;
  architecture: string;
  provenance: string;
  dataset_type: string;
  validation_metric: string;
  probability: number;
  confidence: number;
  risk_level: string;
}

export interface ScreeningResponse {
  request_id: string;
  session_id: string;
  patient_identifier?: string;
  original_filename: string;
  audio_sha256: string;
  risk_level: 'low' | 'uncertain' | 'elevated';
  prediction: 'parkinsons' | 'healthy';
  probability: number;
  confidence: number;
  quality_report: QualityReport;
  primary_model: ModelProvenance;
  secondary_model: ModelProvenance;
  biomarkers: Biomarkers;
  audio_url?: string;
  latency_ms: number;
  stage_latencies?: Record<string, number>;
  disclaimer: string;
  created_at: string;
}

export interface HistoryItem {
  id: string;
  patient_identifier?: string;
  original_filename: string;
  audio_sha256?: string;
  risk_level: 'low' | 'uncertain' | 'elevated';
  prediction: string;
  probability: number;
  confidence: number;
  model_version?: string;
  model_architecture: string;
  quality_report?: QualityReport;
  biomarkers: Record<string, number>;
  disclaimer: string;
  created_at: string;
}

export interface HistoryListResponse {
  total: number;
  items: HistoryItem[];
  disclaimer: string;
}

export interface ProblemDetail {
  type: string;
  title: string;
  status: number;
  detail: string;
  instance?: string;
  request_id?: string;
  quality_report?: QualityReport;
}

const API_BASE = '/api/v1';

export const apiClient = {
  async checkHealth() {
    const res = await fetch(`${API_BASE}/health`);
    if (!res.ok) throw new Error('Health check failed');
    return res.json();
  },

  async checkReady() {
    const res = await fetch(`${API_BASE}/ready`);
    return res.json();
  },

  async screenAudio(
    file: Blob | File,
    filename: string = 'recording.wav',
    patientId?: string,
    consentGiven: boolean = true,
  ): Promise<ScreeningResponse> {
    const formData = new FormData();
    formData.append('file', file, filename);
    if (patientId) {
      formData.append('patient_identifier', patientId);
    }
    formData.append('consent_given', consentGiven ? 'true' : 'false');

    const res = await fetch(`${API_BASE}/screen`, {
      method: 'POST',
      body: formData,
    });

    if (!res.ok) {
      const errJson = await res.json().catch(() => null);
      if (errJson && errJson.title) {
        // Structured RFC 7807 problem details
        const problem = errJson as ProblemDetail;
        const customErr = new Error(problem.detail || problem.title) as any;
        customErr.problemDetail = problem;
        throw customErr;
      }
      throw new Error(errJson?.detail || `Screening request failed with status ${res.status}`);
    }

    return res.json();
  },

  async getHistory(limit: number = 20, offset: number = 0): Promise<HistoryListResponse> {
    const res = await fetch(`${API_BASE}/history?limit=${limit}&offset=${offset}`);
    if (!res.ok) throw new Error('Failed to fetch screening history');
    return res.json();
  },

  async getSession(id: string): Promise<HistoryItem> {
    const res = await fetch(`${API_BASE}/history/${id}`);
    if (!res.ok) throw new Error('Failed to fetch session details');
    return res.json();
  },

  async deleteSession(id: string): Promise<void> {
    const res = await fetch(`${API_BASE}/history/${id}`, {
      method: 'DELETE',
    });
    if (!res.ok && res.status !== 204) {
      throw new Error('Failed to delete screening record');
    }
  },
};
