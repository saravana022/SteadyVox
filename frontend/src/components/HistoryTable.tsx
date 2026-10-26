import React, { useState, useEffect } from 'react';
import { HistoryItem, apiClient } from '../api/client';
import { History, RefreshCw, AlertCircle, CheckCircle2, AlertOctagon, HelpCircle, ShieldAlert, Trash2 } from 'lucide-react';

export const HistoryTable: React.FC = () => {
  const [sessions, setSessions] = useState<HistoryItem[]>([]);
  const [total, setTotal] = useState(0);
  const [loading, setLoading] = useState(true);
  const [deletingId, setDeletingId] = useState<string | null>(null);
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
      setError('Could not retrieve database history.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadHistory(page * pageSize);
  }, [page]);

  const handleDelete = async (id: string) => {
    if (!window.confirm('Are you sure you want to permanently erase this screening session?')) {
      return;
    }
    setDeletingId(id);
    try {
      await apiClient.deleteSession(id);
      setSessions((prev) => prev.filter((s) => s.id !== id));
      setTotal((t) => Math.max(0, t - 1));
    } catch (err: any) {
      alert(`Deletion failed: ${err.message}`);
    } finally {
      setDeletingId(null);
    }
  };

  const getRiskBadge = (risk: string) => {
    switch (risk) {
      case 'low':
        return (
          <span className="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-[11px] font-bold uppercase font-mono bg-emerald-500/15 border border-emerald-500/30 text-emerald-400">
            <CheckCircle2 className="w-3 h-3" /> Low
          </span>
        );
      case 'elevated':
        return (
          <span className="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-[11px] font-bold uppercase font-mono bg-rose-500/15 border border-rose-500/30 text-rose-400">
            <AlertOctagon className="w-3 h-3" /> Elevated
          </span>
        );
      default:
        return (
          <span className="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-[11px] font-bold uppercase font-mono bg-amber-500/15 border border-amber-500/30 text-amber-400">
            <HelpCircle className="w-3 h-3" /> Uncertain
          </span>
        );
    }
  };

  return (
    <div className="space-y-6">
      <div className="card-nixtio p-6 flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
        <div>
          <div className="flex items-center gap-2">
            <History className="w-5 h-5 text-accent" />
            <h2 className="text-xl font-bold tracking-tight text-txt">
              Screening History & Audit Trail
            </h2>
          </div>
          <p className="text-xs text-txt-muted mt-0.5">
            Historical log of clinical acoustic screening sessions (Total: {total})
          </p>
        </div>
        <button
          onClick={() => loadHistory(page * pageSize)}
          disabled={loading}
          className="touch-target px-4 py-2 bg-surface-2 hover:bg-border text-txt rounded-xl text-xs font-semibold flex items-center gap-2 transition border border-border"
        >
          <RefreshCw className={`w-3.5 h-3.5 ${loading ? 'animate-spin text-accent' : ''}`} /> Refresh
        </button>
      </div>

      {/* Mandatory Disclaimer for History */}
      <div className="p-3.5 rounded-xl border border-amber-500/30 bg-amber-500/10 text-amber-400 text-xs flex items-center gap-2">
        <ShieldAlert className="w-4 h-4 flex-shrink-0" />
        <span>
          <strong>Research screening tool only — not a medical diagnosis.</strong> Historical recordings are stored de-identified for longitudinal exploratory triaging.
        </span>
      </div>

      {error && (
        <div className="p-4 rounded-xl bg-red-500/10 border border-red-500/20 text-xs text-red-400 flex items-center gap-2">
          <AlertCircle className="w-4 h-4 flex-shrink-0" />
          <span>{error}</span>
        </div>
      )}

      <div className="card-nixtio overflow-hidden">
        {loading ? (
          <div className="p-16 text-center text-xs text-txt-muted flex flex-col items-center justify-center gap-3">
            <RefreshCw className="w-6 h-6 animate-spin text-accent" />
            <span>Loading historical screening records...</span>
          </div>
        ) : sessions.length === 0 ? (
          <div className="p-16 text-center text-xs text-txt-muted">
            No screening sessions recorded yet. Start a voice test to build your history.
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs text-txt-muted">
              <thead className="bg-surface-2/60 border-b border-border text-[11px] font-bold text-txt uppercase tracking-wider font-mono">
                <tr>
                  <th className="px-5 py-3.5">Timestamp</th>
                  <th className="px-5 py-3.5">Participant ID</th>
                  <th className="px-5 py-3.5">Risk Level</th>
                  <th className="px-5 py-3.5">Confidence</th>
                  <th className="px-5 py-3.5">Jitter / Shimmer / HNR</th>
                  <th className="px-5 py-3.5">Model</th>
                  <th className="px-5 py-3.5 text-right">Erase</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-border/60">
                {sessions.map((s) => {
                  const biomarkers = s.biomarkers || {};
                  return (
                    <tr key={s.id} className="hover:bg-surface-2/40 transition">
                      <td className="px-5 py-4 whitespace-nowrap font-mono text-[11px] text-txt">
                        {s.created_at ? new Date(s.created_at).toLocaleString() : 'N/A'}
                      </td>
                      <td className="px-5 py-4 whitespace-nowrap font-medium text-txt">
                        {s.patient_identifier || s.id.slice(0, 8)}
                      </td>
                      <td className="px-5 py-4 whitespace-nowrap">
                        {getRiskBadge(s.risk_level || (s.prediction === 'parkinsons' ? 'elevated' : 'low'))}
                      </td>
                      <td className="px-5 py-4 whitespace-nowrap font-mono font-bold text-txt">
                        {(s.confidence * 100).toFixed(1)}%
                      </td>
                      <td className="px-5 py-4 whitespace-nowrap font-mono text-[11px] text-txt-muted">
                        J: {biomarkers.jitter_local_percent?.toFixed(2) ?? '-'}% | S: {biomarkers.shimmer_local_percent?.toFixed(2) ?? '-'}% | H: {biomarkers.hnr_mean_db?.toFixed(1) ?? '-'}dB
                      </td>
                      <td className="px-5 py-4 whitespace-nowrap font-mono text-[10px] text-txt-muted uppercase">
                        {s.model_architecture}
                      </td>
                      <td className="px-5 py-4 whitespace-nowrap text-right">
                        <button
                          type="button"
                          onClick={() => handleDelete(s.id)}
                          disabled={deletingId === s.id}
                          aria-label="Delete screening session"
                          className="touch-target p-2 text-txt-muted hover:text-red-400 hover:bg-surface-2 rounded-lg transition"
                          title="Delete session (GDPR erasure)"
                        >
                          <Trash2 className="w-4 h-4" />
                        </button>
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
          <div className="px-5 py-4 bg-surface-2/40 border-t border-border flex items-center justify-between text-xs">
            <span className="text-txt-muted">
              Showing {page * pageSize + 1} to {Math.min((page + 1) * pageSize, total)} of {total} records
            </span>
            <div className="flex items-center gap-2">
              <button
                disabled={page === 0}
                onClick={() => setPage((p) => Math.max(0, p - 1))}
                className="touch-target px-3 py-1.5 border border-border rounded-lg bg-surface hover:bg-surface-2 disabled:opacity-40 transition"
              >
                Previous
              </button>
              <button
                disabled={(page + 1) * pageSize >= total}
                onClick={() => setPage((p) => p + 1)}
                className="touch-target px-3 py-1.5 border border-border rounded-lg bg-surface hover:bg-surface-2 disabled:opacity-40 transition"
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
