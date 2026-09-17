/**
 * SteadyVox Typed API Client
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
}

export interface ScreeningResponse {
  session_id: string;
  patient_identifier?: string;
  original_filename: string;
  prediction: 'parkinsons' | 'healthy';
  probability: number;
  confidence: number;
  model_architecture: string;
  biomarkers: Biomarkers;
  audio_url?: string;
  latency_ms: number;
  disclaimer: string;
  created_at: string;
}

export interface HistoryItem {
  id: string;
  patient_identifier?: string;
  original_filename: string;
  prediction: string;
  probability: number;
  confidence: number;
  model_architecture: string;
  biomarkers: Record<string, number>;
  disclaimer: string;
  created_at: string;
}

export interface HistoryListResponse {
  total: number;
  items: HistoryItem[];
  disclaimer: string;
}

const API_BASE = '/api/v1';

export const apiClient = {
  async checkHealth() {
    const res = await fetch(`${API_BASE}/health`);
    if (!res.ok) throw new Error('Health check failed');
    return res.json();
  },

  async screenAudio(file: Blob | File, filename: string = 'recording.wav', patientId?: string): Promise<ScreeningResponse> {
    const formData = new FormData();
    formData.append('file', file, filename);
    if (patientId) {
      formData.append('patient_identifier', patientId);
    }

    const res = await fetch(`${API_BASE}/screen/upload`, {
      method: 'POST',
      body: formData,
    });

    if (!res.ok) {
      const err = await res.json().catch(() => ({ detail: 'Screening request failed' }));
      throw new Error(err.detail || 'Screening request failed');
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
};
