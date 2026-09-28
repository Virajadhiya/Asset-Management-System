import React, { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { Link } from 'react-router-dom';
import { api } from '../api/endpoints';
import { useAsset, ASSET_DEFINITIONS, AssetType } from '../context/AssetContext';
import { StatusBadge } from '../components/common/StatusBadge';
import { ConditionBadge } from '../components/common/ConditionBadge';

const GUJARAT_DISTRICTS = [
  'Ahmedabad', 'Surat', 'Vadodara', 'Rajkot', 'Bhavnagar',
  'Jamnagar', 'Junagadh', 'Bharuch', 'Banaskantha', 'Mehsana',
  'Amreli', 'Anand', 'Navsari', 'Valsad', 'Morbi', 'Devbhumi Dwarka', 'Gandhinagar', 'Panchmahal', 'Narmada', 'Kheda', 'Porbandar'
];

export default function BridgeList() {
  const { activeAssetType, setAssetType, activeMeta, getMeta } = useAsset();
  const [page, setPage] = useState(1);
  const [search, setSearch] = useState('');
  const [statusFilter, setStatusFilter] = useState('');
  const [districtFilter, setDistrictFilter] = useState('');
  
  const { data, isLoading, isError, error, refetch } = useQuery({
    queryKey: ['bridges', activeAssetType, page, search, statusFilter, districtFilter],
    queryFn: () => api.getBridges({
      page,
      limit: 10,
      asset_type: activeAssetType !== 'ALL' ? activeAssetType : undefined,
      search: search || undefined,
      status: statusFilter || undefined,
      district: districtFilter || undefined,
    }),
  });

  const resetFilters = () => {
    setSearch('');
    setStatusFilter('');
    setDistrictFilter('');
    setPage(1);
  };

  // Safe extraction of items array
  const items: any[] = Array.isArray(data) ? data : (data?.items || []);
  const totalCount: number = data?.total ?? items.length;

  return (
    <div className="space-y-4">
      {/* Portfolio Selector Tabs */}
      <div className="bg-white p-3 rounded-lg shadow-sm border border-slate-200 flex flex-wrap items-center justify-between gap-2">
        <div className="flex items-center gap-2">
          <span className="text-xl">{activeMeta.icon}</span>
          <span className="text-sm font-bold text-slate-800">
            {activeAssetType === 'ALL' ? 'All Infrastructure Assets' : activeMeta.plural}
          </span>
          <span className="text-xs px-2 py-0.5 bg-slate-100 text-slate-600 rounded-full font-mono font-bold">
            {totalCount}
          </span>
        </div>

        <div className="flex items-center gap-1 overflow-x-auto">
          {(['ALL', 'BRIDGE', 'TUNNEL', 'HIGHWAY', 'CULVERT'] as AssetType[]).map((type) => {
            const m = ASSET_DEFINITIONS[type];
            const isSel = activeAssetType === type;
            return (
              <button
                key={type}
                onClick={() => {
                  setAssetType(type);
                  setPage(1);
                }}
                className={`flex items-center gap-1.5 px-2.5 py-1 rounded-md text-xs font-semibold transition-all cursor-pointer ${
                  isSel
                    ? 'bg-blue-600 text-white shadow-xs'
                    : 'bg-slate-100 hover:bg-slate-200 text-slate-600'
                }`}
              >
                <span>{m.icon}</span>
                <span>{m.label}</span>
              </button>
            );
          })}
        </div>
      </div>

      {/* Main Registry Table Card */}
      <div className="bg-white rounded-lg shadow-sm border border-slate-200 overflow-hidden space-y-0">
        {/* Filter Bar */}
        <div className="p-4 border-b border-slate-200 bg-slate-50 flex flex-col md:flex-row justify-between items-start md:items-center gap-3">
          <div>
            <h2 className="text-base font-bold text-slate-800">
              {activeAssetType === 'ALL' ? 'National Infrastructure Master Registry' : `${activeMeta.singular} Master Registry`}
            </h2>
            <p className="text-xs text-slate-500">
              Structural inventory with engineering specifications, GIS coordinates, and live {activeMeta.healthShort} health scores.
            </p>
          </div>
          
          <div className="flex flex-wrap items-center gap-2 w-full md:w-auto">
            <input 
              type="text" 
              placeholder={`Search ${activeMeta.singular.toLowerCase()}...`}
              className="px-3 py-1.5 border border-slate-300 rounded-md text-xs w-full sm:w-48 bg-white"
              value={search}
              onChange={(e) => { setSearch(e.target.value); setPage(1); }}
            />

            <select
              value={statusFilter}
              onChange={(e) => { setStatusFilter(e.target.value); setPage(1); }}
              className="px-2.5 py-1.5 border border-slate-300 rounded-md text-xs bg-white text-slate-700"
            >
              <option value="">All Statuses</option>
              <option value="OPERATIONAL">Operational</option>
              <option value="UNDER_MAINTENANCE">Under Maintenance</option>
              <option value="UNDER_REHABILITATION">Under Rehabilitation</option>
              <option value="CLOSED">Closed</option>
              <option value="UNDER_CONSTRUCTION">Under Construction</option>
              <option value="PLANNED">Planned</option>
            </select>

            <select
              value={districtFilter}
              onChange={(e) => { setDistrictFilter(e.target.value); setPage(1); }}
              className="px-2.5 py-1.5 border border-slate-300 rounded-md text-xs bg-white text-slate-700"
            >
              <option value="">All Districts</option>
              {GUJARAT_DISTRICTS.map(d => (
                <option key={d} value={d}>{d}</option>
              ))}
            </select>

            {(search || statusFilter || districtFilter) && (
              <button
                onClick={resetFilters}
                className="text-xs text-blue-600 hover:text-blue-800 font-semibold px-2 py-1"
              >
                Reset
              </button>
            )}
          </div>
        </div>

        {/* Error state with retry */}
        {isError && (
          <div className="p-6 text-center bg-red-50 border-b border-red-200">
            <div className="text-sm font-semibold text-red-700 mb-1">
              Failed to load assets registry.
            </div>
            <p className="text-xs text-red-500 mb-3">
              {(error as any)?.response?.data?.detail || (error as any)?.message || 'Permission denied or network error.'}
            </p>
            <button
              onClick={() => refetch()}
              className="px-3 py-1 bg-red-600 text-white rounded text-xs font-semibold hover:bg-red-700"
            >
              Retry Request
            </button>
          </div>
        )}
        
        {/* Table */}
        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-slate-200">
            <thead className="bg-slate-50">
              <tr>
                <th className="px-5 py-3 text-left text-[11px] font-bold text-slate-500 uppercase tracking-wider">Asset Code</th>
                <th className="px-5 py-3 text-left text-[11px] font-bold text-slate-500 uppercase tracking-wider">Name & Route</th>
                <th className="px-5 py-3 text-left text-[11px] font-bold text-slate-500 uppercase tracking-wider">Class</th>
                <th className="px-5 py-3 text-left text-[11px] font-bold text-slate-500 uppercase tracking-wider">District</th>
                <th className="px-5 py-3 text-left text-[11px] font-bold text-slate-500 uppercase tracking-wider">Status</th>
                <th className="px-5 py-3 text-left text-[11px] font-bold text-slate-500 uppercase tracking-wider">Condition</th>
                <th className="px-5 py-3 text-left text-[11px] font-bold text-slate-500 uppercase tracking-wider">{activeMeta.healthShort}</th>
                <th className="px-5 py-3 text-right text-[11px] font-bold text-slate-500 uppercase tracking-wider">Action</th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-slate-200">
              {isLoading ? (
                <tr><td colSpan={8} className="px-6 py-10 text-center text-slate-500 text-sm">Loading registry data...</td></tr>
              ) : items.length === 0 ? (
                <tr><td colSpan={8} className="px-6 py-10 text-center text-slate-400 text-sm">No assets found matching criteria.</td></tr>
              ) : items.map((bridge: any) => {
                const bId = bridge.bridge_id || bridge.id;
                const bCode = bridge.bridge_code || bridge.bridge_id_str || 'ID-UNKNOWN';
                const bName = bridge.bridge_name || bridge.name || 'Unnamed Asset';
                const aType = bridge.asset_type || 'BRIDGE';
                const meta = getMeta(aType);
                const bStatus = bridge.current_status || bridge.status || 'PLANNED';
                const bCond = bridge.latest_condition_category || bridge.condition || null;
                const bHealth = bridge.latest_health_index ?? bridge.health_index ?? null;

                return (
                  <tr key={bId} className="hover:bg-slate-50 transition-colors">
                    <td className="px-5 py-3.5 whitespace-nowrap text-xs font-mono font-bold text-blue-600">
                      <Link to={`/bridges/${bId}`} className="hover:underline">
                        {bCode}
                      </Link>
                    </td>
                    <td className="px-5 py-3.5 whitespace-nowrap">
                      <Link to={`/bridges/${bId}`} className="text-sm font-semibold text-slate-800 hover:text-blue-600 block">
                        {bName}
                      </Link>
                      {bridge.road_name && (
                        <div className="text-[11px] text-slate-400 line-clamp-1">{bridge.road_name}</div>
                      )}
                    </td>
                    <td className="px-5 py-3.5 whitespace-nowrap">
                      <span className="inline-flex items-center gap-1 px-2 py-0.5 bg-slate-100 text-slate-700 rounded text-[11px] font-semibold border border-slate-200">
                        <span>{meta.icon}</span>
                        <span>{meta.singular}</span>
                      </span>
                    </td>
                    <td className="px-5 py-3.5 whitespace-nowrap text-xs text-slate-600 font-medium">{bridge.district || 'N/A'}</td>
                    <td className="px-5 py-3.5 whitespace-nowrap"><StatusBadge status={bStatus} /></td>
                    <td className="px-5 py-3.5 whitespace-nowrap"><ConditionBadge condition={bCond} /></td>
                    <td className="px-5 py-3.5 whitespace-nowrap text-sm font-black text-slate-800">
                      {bHealth != null ? `${bHealth}` : '-'}
                    </td>
                    <td className="px-5 py-3.5 whitespace-nowrap text-right text-xs">
                      <Link
                        to={`/bridges/${bId}`}
                        className="text-blue-600 hover:text-blue-800 font-semibold inline-flex items-center gap-1"
                      >
                        Inspect &rarr;
                      </Link>
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
        
        {/* Pagination Footer */}
        <div className="px-5 py-3.5 border-t border-slate-200 bg-slate-50 flex items-center justify-between text-xs text-slate-600">
          <span>
            Showing {items.length > 0 ? ((page - 1) * 10) + 1 : 0} to {Math.min(page * 10, totalCount)} of {totalCount} registered assets
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
              disabled={page * 10 >= totalCount} 
              onClick={() => setPage(p => p + 1)}
              className="px-3 py-1 border border-slate-300 rounded bg-white font-medium hover:bg-slate-50 disabled:opacity-40"
            >
              Next
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}