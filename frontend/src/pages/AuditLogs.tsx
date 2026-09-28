import React, { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { api } from '../api/endpoints';

export default function AuditLogs() {
  const [page, setPage] = useState(1);
  const [entityFilter, setEntityFilter] = useState('');
  const [selectedLog, setSelectedLog] = useState<any | null>(null);

  const { data, isLoading, isError, error, refetch } = useQuery({
    queryKey: ['audit-logs', page, entityFilter],
    queryFn: () => api.getAuditLogs({
      page,
      limit: 20,
      entity_type: entityFilter || undefined,
    }),
  });

  const logs: any[] = Array.isArray(data) ? data : (data?.items || []);
  const totalCount: number = data?.total ?? logs.length;

  return (
    <div className="space-y-6">
      <div className="bg-white p-6 rounded-lg shadow-sm border border-slate-200 flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
        <div>
          <div className="text-xs font-bold uppercase tracking-wider text-blue-600">Compliance & Security</div>
          <h1 className="text-2xl font-bold text-slate-900 mt-1">Immutable Audit Trail</h1>
          <p className="text-xs text-slate-500 mt-0.5">
            System logs recording every create, update, and delete action across all bridge lifecycle entities.
          </p>
        </div>

        <div className="flex items-center gap-3">
          <select
            value={entityFilter}
            onChange={(e) => { setEntityFilter(e.target.value); setPage(1); }}
            className="px-3 py-1.5 border border-slate-300 rounded text-xs bg-white text-slate-700"
          >
            <option value="">All Entities</option>
            <option value="bridge">Bridges</option>
            <option value="inspection">Inspections</option>
            <option value="maintenance">Maintenance</option>
            <option value="lifecycle">Lifecycle</option>
          </select>

          {entityFilter && (
            <button
              onClick={() => { setEntityFilter(''); setPage(1); }}
              className="text-xs text-blue-600 hover:text-blue-800 font-semibold"
            >
              Reset
            </button>
          )}
        </div>
      </div>

      {isError && (
        <div className="p-6 bg-red-50 border border-red-200 rounded-lg text-center space-y-2">
          <div className="text-sm font-semibold text-red-700">Access Denied or Failed to Load Audit Logs</div>
          <p className="text-xs text-red-500">
            {(error as any)?.response?.data?.detail || 'Only Administrator and Department Head roles can view audit trails.'}
          </p>
          <button
            onClick={() => refetch()}
            className="px-3 py-1 bg-red-600 text-white rounded text-xs font-semibold hover:bg-red-700"
          >
            Retry
          </button>
        </div>
      )}

      <div className="bg-white rounded-lg shadow-sm border border-slate-200 overflow-hidden">
        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-slate-200">
            <thead className="bg-slate-50">
              <tr>
                <th className="px-5 py-3 text-left text-[11px] font-bold text-slate-500 uppercase tracking-wider">Timestamp</th>
                <th className="px-5 py-3 text-left text-[11px] font-bold text-slate-500 uppercase tracking-wider">Action</th>
                <th className="px-5 py-3 text-left text-[11px] font-bold text-slate-500 uppercase tracking-wider">Entity</th>
                <th className="px-5 py-3 text-left text-[11px] font-bold text-slate-500 uppercase tracking-wider">Performed By</th>
                <th className="px-5 py-3 text-left text-[11px] font-bold text-slate-500 uppercase tracking-wider">Entity ID</th>
                <th className="px-5 py-3 text-right text-[11px] font-bold text-slate-500 uppercase tracking-wider">Payload Diff</th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-slate-200">
              {isLoading ? (
                <tr><td colSpan={6} className="px-6 py-10 text-center text-slate-500 text-sm">Loading audit records...</td></tr>
              ) : logs.length === 0 ? (
                <tr><td colSpan={6} className="px-6 py-10 text-center text-slate-400 text-sm">No audit logs found matching criteria.</td></tr>
              ) : logs.map((log: any) => {
                const actionColor =
                  log.action === 'CREATE' ? 'bg-emerald-100 text-emerald-800 border-emerald-200' :
                  log.action === 'UPDATE' ? 'bg-amber-100 text-amber-800 border-amber-200' :
                  'bg-red-100 text-red-800 border-red-200';

                return (
                  <tr key={log.id} className="hover:bg-slate-50 transition-colors">
                    <td className="px-5 py-3.5 whitespace-nowrap text-xs text-slate-600 font-mono">
                      {log.timestamp || 'N/A'}
                    </td>
                    <td className="px-5 py-3.5 whitespace-nowrap">
                      <span className={`px-2 py-0.5 rounded text-[11px] font-bold border ${actionColor}`}>
                        {log.action}
                      </span>
                    </td>
                    <td className="px-5 py-3.5 whitespace-nowrap text-xs font-semibold text-slate-800 capitalize">
                      {log.entity_type}
                    </td>
                    <td className="px-5 py-3.5 whitespace-nowrap text-xs text-slate-700">
                      <span className="font-semibold">{log.user_name || 'System'}</span>
                      {log.user_role && (
                        <span className="ml-1.5 px-1.5 py-0.5 bg-slate-100 text-slate-600 rounded text-[10px]">
                          {log.user_role}
                        </span>
                      )}
                    </td>
                    <td className="px-5 py-3.5 whitespace-nowrap font-mono text-[11px] text-slate-400">
                      {log.entity_id ? `${log.entity_id.slice(0, 13)}...` : '-'}
                    </td>
                    <td className="px-5 py-3.5 whitespace-nowrap text-right">
                      <button
                        onClick={() => setSelectedLog(log)}
                        className="text-xs font-semibold text-blue-600 hover:text-blue-800 hover:underline"
                      >
                        Inspect Payload &rarr;
                      </button>
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>

        {/* Pagination */}
        <div className="px-5 py-3.5 border-t border-slate-200 bg-slate-50 flex items-center justify-between text-xs text-slate-600">
          <span>
            Showing {logs.length > 0 ? ((page - 1) * 20) + 1 : 0} to {Math.min(page * 20, totalCount)} of {totalCount} audit entries
          </span>
          <div className="flex gap-2">
            <button
              disabled={page === 1}
              onClick={() => setPage(p => Math.max(1, p - 1))}
              className="px-3 py-1 border border-slate-300 rounded bg-white font-medium hover:bg-slate-50 disabled:opacity-40"
            >
              Previous
            </button>
            <button
              disabled={page * 20 >= totalCount}
              onClick={() => setPage(p => p + 1)}
              className="px-3 py-1 border border-slate-300 rounded bg-white font-medium hover:bg-slate-50 disabled:opacity-40"
            >
              Next
            </button>
          </div>
        </div>
      </div>

      {/* Payload Modal */}
      {selectedLog && (
        <div className="fixed inset-0 bg-black/40 z-50 flex items-center justify-center p-4">
          <div className="bg-white rounded-lg max-w-2xl w-full p-6 space-y-4 shadow-xl max-h-[85vh] flex flex-col">
            <div className="flex justify-between items-center border-b border-slate-100 pb-3">
              <div>
                <h3 className="text-base font-bold text-slate-900">
                  Audit Record: {selectedLog.action} {selectedLog.entity_type.toUpperCase()}
                </h3>
                <p className="text-xs text-slate-400 font-mono mt-0.5">ID: {selectedLog.entity_id}</p>
              </div>
              <button
                onClick={() => setSelectedLog(null)}
                className="text-slate-400 hover:text-slate-600 text-lg font-bold"
              >
                &times;
              </button>
            </div>

            <div className="flex-1 overflow-y-auto space-y-4 text-xs font-mono">
              {selectedLog.old_value && (
                <div>
                  <div className="text-[11px] font-bold uppercase text-red-600 font-sans mb-1">Previous State (Old Value)</div>
                  <pre className="p-3 bg-red-50/50 border border-red-200 rounded text-slate-800 overflow-x-auto text-[11px]">
                    {JSON.stringify(selectedLog.old_value, null, 2)}
                  </pre>
                </div>
              )}

              {selectedLog.new_value && (
                <div>
                  <div className="text-[11px] font-bold uppercase text-emerald-600 font-sans mb-1">New State (New Value)</div>
                  <pre className="p-3 bg-emerald-50/50 border border-emerald-200 rounded text-slate-800 overflow-x-auto text-[11px]">
                    {JSON.stringify(selectedLog.new_value, null, 2)}
                  </pre>
                </div>
              )}

              {!selectedLog.old_value && !selectedLog.new_value && (
                <div className="text-center py-6 text-slate-400 text-xs font-sans">
                  No additional JSON payload stored for this entry.
                </div>
              )}
            </div>

            <div className="flex justify-end pt-3 border-t border-slate-100">
              <button
                onClick={() => setSelectedLog(null)}
                className="px-4 py-1.5 bg-slate-100 hover:bg-slate-200 text-slate-700 rounded text-xs font-semibold"
              >
                Close
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
