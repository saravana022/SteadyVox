import React, { useState, useEffect } from 'react';
import { HistoryItem, apiClient } from '../api/client';
import { History, RefreshCw, AlertCircle, CheckCircle2, AlertOctagon, ShieldAlert } from 'lucide-react';

export const HistoryTable: React.FC = () => {
  const [sessions, setSessions] = useState<HistoryItem[]>([]);
  const [total, setTotal] = useState(0);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [page, setPage] = useState(0);
  const pageSize = 10;

  const loadHistory = async (offset = 0) => {
    setLoading(true);
    setError(null);
    try {
      const data = await apiClient.getHistory(pageSize, offset);
      setSessions(data.items);
      setTotal(data.total);
    } catch (err: any) {
      console.error(err);
      setError('Could not connect to database history. Showing local active session state.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadHistory(page * pageSize);
  }, [page]);

  return (
    <div className="space-y-6">
      <div className="bg-white rounded-xl border border-slate-200 p-6 shadow-sm flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
        <div>
          <h2 className="text-lg font-bold text-slate-900 flex items-center gap-2">
            <History className="w-5 h-5 text-teal-600" />
            Screening Session History
          </h2>
          <p className="text-xs text-slate-500 mt-0.5">
            Log of voice analyses and acoustic biomarker extractions (Total: {total})
          </p>
        </div>
        <button
          onClick={() => loadHistory(page * pageSize)}
          disabled={loading}
          className="px-3.5 py-1.5 bg-slate-100 hover:bg-slate-200 text-slate-700 rounded-lg text-xs font-medium flex items-center gap-1.5 transition"
        >
          <RefreshCw className={`w-3.5 h-3.5 ${loading ? 'animate-spin' : ''}`} /> Refresh
        </button>
      </div>

      {/* Mandatory Disclaimer for History */}
      <div className="p-3 bg-amber-50 border border-amber-200 rounded-lg text-amber-900 text-xs flex items-center gap-2">
        <ShieldAlert className="w-4 h-4 text-amber-600 flex-shrink-0" />
        <span>
          <strong>Research screening tool only — not a medical diagnosis.</strong> Historical records are strictly for exploratory triage and clinical study.
        </span>
      </div>

      {error && (
        <div className="p-4 bg-red-50 text-red-700 text-xs rounded-xl border border-red-200 flex items-center gap-2">
          <AlertCircle className="w-4 h-4 flex-shrink-0" />
          <span>{error}</span>
        </div>
      )}

      <div className="bg-white rounded-xl border border-slate-200 overflow-hidden shadow-sm">
        {loading ? (
          <div className="p-12 text-center text-xs text-slate-500 flex flex-col items-center justify-center gap-2">
            <RefreshCw className="w-6 h-6 animate-spin text-teal-600" />
            <span>Loading screening history...</span>
          </div>
        ) : sessions.length === 0 ? (
          <div className="p-12 text-center text-xs text-slate-500">
            No screening sessions recorded yet. Record or upload an audio sample to start.
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs text-slate-600">
              <thead className="bg-slate-50 border-b border-slate-200 text-[11px] font-semibold text-slate-700 uppercase tracking-wider">
                <tr>
                  <th className="px-4 py-3">Date</th>
                  <th className="px-4 py-3">Patient ID</th>
                  <th className="px-4 py-3">Filename</th>
                  <th className="px-4 py-3">Result</th>
                  <th className="px-4 py-3">Confidence</th>
                  <th className="px-4 py-3">Jitter / Shimmer / HNR</th>
                  <th className="px-4 py-3 text-right">Model</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100">
                {sessions.map((s) => {
                  const isPd = s.prediction === 'parkinsons';
                  const biomarkers = s.biomarkers || {};
                  return (
                    <tr key={s.id} className="hover:bg-slate-50/70 transition">
                      <td className="px-4 py-3 whitespace-nowrap font-mono text-[11px]">
                        {s.created_at ? new Date(s.created_at).toLocaleString() : 'N/A'}
                      </td>
                      <td className="px-4 py-3 whitespace-nowrap font-medium text-slate-900">
                        {s.patient_identifier || s.id.slice(0, 8)}
                      </td>
                      <td className="px-4 py-3 max-w-[140px] truncate text-slate-500" title={s.original_filename}>
                        {s.original_filename}
                      </td>
                      <td className="px-4 py-3 whitespace-nowrap">
                        <span
                          className={`inline-flex items-center gap-1 px-2 py-0.5 rounded text-[11px] font-semibold ${
                            isPd ? 'bg-rose-100 text-rose-800' : 'bg-emerald-100 text-emerald-800'
                          }`}
                        >
                          {isPd ? <AlertOctagon className="w-3 h-3" /> : <CheckCircle2 className="w-3 h-3" />}
                          {isPd ? 'PD Indicators' : 'Healthy Profile'}
                        </span>
                      </td>
                      <td className="px-4 py-3 whitespace-nowrap font-mono font-bold text-slate-800">
                        {(s.confidence * 100).toFixed(1)}%
                      </td>
                      <td className="px-4 py-3 whitespace-nowrap font-mono text-[11px] text-slate-500">
                        J: {biomarkers.jitter_local_percent?.toFixed(2) ?? '-'}% | S: {biomarkers.shimmer_local_percent?.toFixed(2) ?? '-'}% | H: {biomarkers.hnr_mean_db?.toFixed(1) ?? '-'}dB
                      </td>
                      <td className="px-4 py-3 whitespace-nowrap text-right font-mono text-[10px] text-slate-400 uppercase">
                        {s.model_architecture}
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        )}

        {/* Pagination Controls */}
        {total > pageSize && (
          <div className="px-4 py-3 bg-slate-50 border-t border-slate-200 flex items-center justify-between text-xs">
            <span className="text-slate-500">
              Showing {page * pageSize + 1} to {Math.min((page + 1) * pageSize, total)} of {total} records
            </span>
            <div className="flex items-center gap-2">
              <button
                disabled={page === 0}
                onClick={() => setPage((p) => Math.max(0, p - 1))}
                className="px-2.5 py-1 border border-slate-300 rounded hover:bg-white disabled:opacity-40 transition"
              >
                Previous
              </button>
              <button
                disabled={(page + 1) * pageSize >= total}
                onClick={() => setPage((p) => p + 1)}
                className="px-2.5 py-1 border border-slate-300 rounded hover:bg-white disabled:opacity-40 transition"
              >
                Next
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};
