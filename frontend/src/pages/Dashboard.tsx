import React from 'react';
import { useQuery } from '@tanstack/react-query';
import { api } from '../api/endpoints';
import { useAsset, ASSET_DEFINITIONS, AssetType } from '../context/AssetContext';
import { StatusBadge } from '../components/common/StatusBadge';
import { ConditionBadge } from '../components/common/ConditionBadge';
import { PriorityBadge } from '../components/common/PriorityBadge';
import { PieChart, Pie, Cell, BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer } from 'recharts';
import { Link } from 'react-router-dom';

const CONDITION_COLORS = {
  EXCELLENT: '#22c55e',
  GOOD: '#3b82f6',
  FAIR: '#eab308',
  POOR: '#f97316',
  CRITICAL: '#ef4444'
};

export default function Dashboard() {
  const { activeAssetType, setAssetType, activeMeta, getMeta } = useAsset();

  const { data: summary, isLoading: loadingSummary, isError: isErrorSummary, refetch: refetchSummary } = useQuery({
    queryKey: ['dashboard-summary', activeAssetType],
    queryFn: () => api.getDashboardSummary({ asset_type: activeAssetType }),
    refetchInterval: 30000
  });

  const { data: rawPriorityList, isLoading: loadingPriority, refetch: refetchPriority } = useQuery({
    queryKey: ['dashboard-priority', activeAssetType],
    queryFn: () => api.getPriorityList({ asset_type: activeAssetType }),
    refetchInterval: 30000
  });

  if (loadingSummary || loadingPriority) {
    return <div className="p-8 text-center text-slate-500">Loading dashboard data...</div>;
  }

  if (isErrorSummary || !summary) {
    return (
      <div className="p-8 bg-white rounded-lg border border-red-200 text-center space-y-3">
        <h3 className="text-base font-bold text-red-600">Failed to load dashboard metrics</h3>
        <p className="text-xs text-slate-500">Unable to retrieve summary data for the current user session.</p>
        <button
          onClick={() => { refetchSummary(); refetchPriority(); }}
          className="px-4 py-2 bg-blue-600 text-white rounded text-xs font-semibold hover:bg-blue-700"
        >
          Retry Loading
        </button>
      </div>
    );
  }

  // Safe data extraction
  const conditionData = Object.entries(summary?.by_condition || {}).map(([name, value]) => ({ name, value }));
  const statusData = Object.entries(summary?.by_status || {}).map(([name, value]) => ({ name, value }));
  const priorityList: any[] = Array.isArray(rawPriorityList) ? rawPriorityList : (rawPriorityList?.items || []);
  const recentEvents: any[] = summary?.recent_events || [];
  const totalAssetsCount = summary.total_assets ?? summary.total_bridges ?? 0;

  return (
    <div className="space-y-6">
      {/* Portfolio Selector Quick Bar */}
      <div className="bg-white p-4 rounded-xl shadow-sm border border-slate-200 flex flex-wrap items-center justify-between gap-3">
        <div className="flex items-center gap-3">
          <span className="text-2xl p-2 bg-slate-50 border border-slate-100 rounded-xl leading-none">{activeMeta.icon}</span>
          <div>
            <div className="text-sm font-black text-slate-900 flex items-center gap-2">
              <span>{activeMeta.label} Portfolio</span>
              <span className={`text-[10px] px-2 py-0.5 rounded-full font-bold uppercase ${activeMeta.badgeBg} ${activeMeta.badgeText}`}>
                {activeAssetType}
              </span>
            </div>
            <div className="text-xs text-slate-500 mt-0.5">{activeMeta.description}</div>
          </div>
        </div>

        <div className="flex items-center gap-1.5 overflow-x-auto py-1">
          {(['ALL', 'BRIDGE', 'TUNNEL', 'HIGHWAY', 'CULVERT'] as AssetType[]).map((type) => {
            const m = ASSET_DEFINITIONS[type];
            const isSel = activeAssetType === type;
            const count = type === 'ALL'
              ? (summary?.total_assets || 45)
              : (summary?.by_asset_type?.[type] ?? (type === 'BRIDGE' ? 30 : 5));
            return (
              <button
                key={type}
                onClick={() => setAssetType(type)}
                className={`flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-bold transition-all cursor-pointer ${
                  isSel
                    ? 'bg-slate-900 text-white shadow-sm ring-2 ring-blue-500/20'
                    : 'bg-slate-100 hover:bg-slate-200 text-slate-700'
                }`}
              >
                <span>{m.icon}</span>
                <span>{m.label}</span>
                <span className={`px-1.5 py-0.2 rounded-full text-[10px] font-mono ${isSel ? 'bg-slate-700 text-white' : 'bg-white text-slate-600'}`}>
                  {count}
                </span>
              </button>
            );
          })}
        </div>
      </div>

      {/* KPI Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className="bg-white p-6 rounded-lg shadow-sm border-l-4 border-blue-500">
          <div className="text-slate-500 text-xs uppercase font-bold tracking-wider">
            Total {activeAssetType === 'ALL' ? 'Assets' : activeMeta.plural}
          </div>
          <div className="mt-2 text-3xl font-black text-slate-800">{totalAssetsCount}</div>
        </div>
        <div className="bg-white p-6 rounded-lg shadow-sm border-l-4 border-emerald-500">
          <div className="text-slate-500 text-xs uppercase font-bold tracking-wider">Operational</div>
          <div className="mt-2 text-3xl font-black text-slate-800">
            {summary.by_status?.['OPERATIONAL'] ?? 0}
          </div>
        </div>
        <div className="bg-white p-6 rounded-lg shadow-sm border-l-4 border-red-500">
          <div className="text-slate-500 text-xs uppercase font-bold tracking-wider">
            Critical {activeAssetType === 'ALL' ? 'Assets' : activeMeta.plural}
          </div>
          <div className="mt-2 text-3xl font-black text-slate-800">
            {summary.critical_bridges_count ?? (summary as any).critical_count ?? 0}
          </div>
        </div>
        <div className="bg-white p-6 rounded-lg shadow-sm border-l-4 border-amber-500">
          <div className="text-slate-500 text-xs uppercase font-bold tracking-wider">Under Maintenance / Rehab</div>
          <div className="mt-2 text-3xl font-black text-slate-800">
            {(summary.by_status?.['UNDER_MAINTENANCE'] ?? 0) + (summary.by_status?.['UNDER_REHABILITATION'] ?? 0)}
          </div>
        </div>
      </div>

      {/* Charts Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="bg-white p-6 rounded-lg shadow-sm border border-slate-200">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-base font-bold text-slate-800">Health Condition Distribution</h3>
            <span className="text-xs font-semibold px-2 py-0.5 bg-slate-100 text-slate-600 rounded">
              {activeMeta.healthShort} Scale
            </span>
          </div>
          <div className="h-64">
            {conditionData.length === 0 ? (
              <div className="h-full flex items-center justify-center text-xs text-slate-400">No condition assessments available.</div>
            ) : (
              <ResponsiveContainer width="100%" height="100%">
                <PieChart>
                  <Pie data={conditionData} dataKey="value" nameKey="name" cx="50%" cy="50%" outerRadius={80} label>
                    {conditionData.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={CONDITION_COLORS[entry.name as keyof typeof CONDITION_COLORS] || '#cbd5e1'} />
                    ))}
                  </Pie>
                  <Tooltip />
                </PieChart>
              </ResponsiveContainer>
            )}
          </div>
        </div>
        
        <div className="bg-white p-6 rounded-lg shadow-sm border border-slate-200">
          <h3 className="text-base font-bold text-slate-800 mb-4">Operational Status Distribution</h3>
          <div className="h-64">
            {statusData.length === 0 ? (
              <div className="h-full flex items-center justify-center text-xs text-slate-400">No status data available.</div>
            ) : (
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={statusData}>
                  <XAxis dataKey="name" tick={{fontSize: 10}} interval={0} angle={-30} textAnchor="end" height={60} />
                  <YAxis />
                  <Tooltip />
                  <Bar dataKey="value" fill="#3b82f6" radius={[4, 4, 0, 0]} />
                </BarChart>
              </ResponsiveContainer>
            )}
          </div>
        </div>
      </div>

      {/* Priority & Activity */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2 bg-white rounded-lg shadow-sm border border-slate-200 overflow-hidden">
          <div className="px-6 py-4 border-b border-slate-200 bg-slate-50">
            <h3 className="text-base font-bold text-slate-800">Priority Attention Registry</h3>
            <p className="text-xs text-slate-500">
              {activeAssetType === 'ALL' ? 'Infrastructure assets' : activeMeta.plural} prioritized for intervention based on condition, distress, and traffic weight.
            </p>
          </div>
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-slate-200">
              <thead className="bg-slate-50">
                <tr>
                  <th className="px-5 py-3 text-left text-[11px] font-bold text-slate-500 uppercase tracking-wider">Asset</th>
                  <th className="px-5 py-3 text-left text-[11px] font-bold text-slate-500 uppercase tracking-wider">Type</th>
                  <th className="px-5 py-3 text-left text-[11px] font-bold text-slate-500 uppercase tracking-wider">District</th>
                  <th className="px-5 py-3 text-left text-[11px] font-bold text-slate-500 uppercase tracking-wider">{activeMeta.healthShort}</th>
                  <th className="px-5 py-3 text-left text-[11px] font-bold text-slate-500 uppercase tracking-wider">Condition</th>
                  <th className="px-5 py-3 text-left text-[11px] font-bold text-slate-500 uppercase tracking-wider">Priority</th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-slate-200">
                {priorityList.map((item: any) => {
                  const bId = item.bridge_id || item.id;
                  const bCode = item.bridge_code || 'ID-UNKNOWN';
                  const bName = item.bridge_name || item.name || 'Unnamed Asset';
                  const bType = item.asset_type || 'BRIDGE';
                  const meta = getMeta(bType);
                  const bDist = item.district || 'Gujarat';
                  const bHealth = item.health_index ?? '-';
                  const bCond = item.condition_category || 'GOOD';
                  const bPrio = item.priority || 'MEDIUM';

                  return (
                    <tr key={bId} className="hover:bg-slate-50">
                      <td className="px-5 py-3.5 whitespace-nowrap">
                        <Link to={`/bridges/${bId}`} className="text-blue-600 hover:text-blue-900 font-mono text-xs font-bold">
                          {bCode}
                        </Link>
                        <div className="text-xs text-slate-600 font-medium">{bName}</div>
                      </td>
                      <td className="px-5 py-3.5 whitespace-nowrap">
                        <span className="inline-flex items-center gap-1 px-2 py-0.5 bg-slate-100 text-slate-700 rounded text-[11px] font-semibold border border-slate-200">
                          <span>{meta.icon}</span>
                          <span>{meta.singular}</span>
                        </span>
                      </td>
                      <td className="px-5 py-3.5 whitespace-nowrap text-xs text-slate-600">{bDist}</td>
                      <td className="px-5 py-3.5 whitespace-nowrap text-sm font-black text-slate-900">{bHealth}</td>
                      <td className="px-5 py-3.5 whitespace-nowrap"><ConditionBadge condition={bCond} /></td>
                      <td className="px-5 py-3.5 whitespace-nowrap"><PriorityBadge priority={bPrio} /></td>
                    </tr>
                  );
                })}
                {priorityList.length === 0 && (
                  <tr>
                    <td colSpan={6} className="px-6 py-6 text-center text-sm text-slate-400">
                      No priority alerts for this asset class at this time.
                    </td>
                  </tr>
                )}
              </tbody>
            </table>
          </div>
        </div>

        {/* Recent Activity */}
        <div className="bg-white rounded-lg shadow-sm border border-slate-200 overflow-hidden flex flex-col h-full">
          <div className="px-6 py-4 border-b border-slate-200 bg-slate-50 flex-shrink-0">
            <h3 className="text-base font-bold text-slate-800">Recent Lifecycle Activity</h3>
          </div>
          <div className="p-4 space-y-3.5 flex-1 overflow-y-auto min-h-0">
            {recentEvents.length === 0 ? (
              <div className="text-center py-6 text-xs text-slate-400">No recent lifecycle events recorded.</div>
            ) : (
              recentEvents.map((event: any, idx: number) => {
                const eventId = event.event_id || `evt-${idx}`;
                const eventType = event.event_type || 'LIFECYCLE_EVENT';
                const eventDate = event.event_date ? new Date(event.event_date).toLocaleDateString() : 'Recent';
                const bridgeCode = event.bridge_code || '';
                const aType = event.asset_type || 'BRIDGE';
                const meta = getMeta(aType);

                return (
                  <div key={eventId} className="border-l-2 border-blue-500 pl-3">
                    <div className="flex items-center gap-1.5">
                      <span className="text-xs font-bold text-slate-800">{eventType.replace(/_/g, ' ')}</span>
                      <span className="text-[10px] px-1.5 py-0.2 bg-slate-100 text-slate-600 rounded">
                        {meta.icon}
                      </span>
                    </div>
                    <div className="text-[11px] text-slate-400 mt-0.5">
                      {eventDate} {bridgeCode && <>&bull; <span className="font-mono">{bridgeCode}</span></>}
                    </div>
                    <div className="text-xs text-slate-600 mt-1 line-clamp-2">{event.description}</div>
                  </div>
                );
              })
            )}
          </div>
        </div>
      </div>
    </div>
  );
}