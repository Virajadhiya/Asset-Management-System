import React, { useState, useRef, useEffect } from 'react';
import { useAsset, ASSET_DEFINITIONS, AssetType } from '../../context/AssetContext';
import { useQuery } from '@tanstack/react-query';
import { api } from '../../api/endpoints';

export const AssetSwitcher: React.FC = () => {
  const { activeAssetType, setAssetType, activeMeta } = useAsset();
  const [isOpen, setIsOpen] = useState(false);
  const dropdownRef = useRef<HTMLDivElement>(null);

  // Fetch summary counts for dropdown badges
  const { data: summary } = useQuery({
    queryKey: ['dashboard-summary', 'counts-only'],
    queryFn: () => api.getDashboardSummary({ asset_type: 'ALL' }),
    staleTime: 60000,
  });

  const counts: Record<AssetType, number> = {
    ALL: (summary as any)?.total_assets || 45,
    BRIDGE: (summary as any)?.by_asset_type?.BRIDGE ?? 30,
    TUNNEL: (summary as any)?.by_asset_type?.TUNNEL ?? 5,
    HIGHWAY: (summary as any)?.by_asset_type?.HIGHWAY ?? 5,
    CULVERT: (summary as any)?.by_asset_type?.CULVERT ?? 5,
  };

  useEffect(() => {
    function handleClickOutside(event: MouseEvent) {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target as Node)) {
        setIsOpen(false);
      }
    }
    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  const assetOptions: AssetType[] = ['ALL', 'BRIDGE', 'TUNNEL', 'HIGHWAY', 'CULVERT'];

  return (
    <div className="relative" ref={dropdownRef}>
      {/* Trigger Button */}
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="flex items-center gap-2.5 px-3 py-1.5 bg-slate-100 hover:bg-slate-200 border border-slate-300 rounded-lg text-xs font-semibold text-slate-800 transition-all shadow-sm"
        title="Switch Infrastructure Asset Portfolio"
      >
        <span className="text-base leading-none">{activeMeta.icon}</span>
        <div className="text-left hidden sm:block">
          <div className="text-[10px] text-slate-500 uppercase tracking-wider font-bold leading-none">Portfolio Asset</div>
          <div className="font-bold text-slate-900 leading-tight flex items-center gap-1.5">
            <span>{activeMeta.label}</span>
            <span className="px-1.5 py-0.2 bg-white text-slate-700 rounded-full border border-slate-200 text-[10px] font-mono">
              {counts[activeAssetType]}
            </span>
          </div>
        </div>
        <svg
          className={`w-3.5 h-3.5 text-slate-500 transition-transform ${isOpen ? 'rotate-180' : ''}`}
          fill="none"
          stroke="currentColor"
          viewBox="0 0 24 24"
        >
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
        </svg>
      </button>

      {/* Dropdown Menu */}
      {isOpen && (
        <div className="absolute right-0 mt-2 w-72 bg-white rounded-xl shadow-xl border border-slate-200 py-2 z-50 animate-in fade-in slide-in-from-top-1 duration-150">
          <div className="px-3.5 py-2 border-b border-slate-100">
            <div className="text-xs font-bold text-slate-900">Select Infrastructure Asset Class</div>
            <div className="text-[11px] text-slate-500">Filters dashboard, registry, and spatial GIS view</div>
          </div>

          <div className="p-1 space-y-1">
            {assetOptions.map((type) => {
              const meta = ASSET_DEFINITIONS[type];
              const isSelected = activeAssetType === type;
              const count = counts[type];

              return (
                <button
                  key={type}
                  onClick={() => {
                    setAssetType(type);
                    setIsOpen(false);
                  }}
                  className={`w-full text-left px-3 py-2 rounded-lg flex items-center justify-between text-xs transition-colors ${
                    isSelected
                      ? 'bg-blue-50 text-blue-900 font-bold border border-blue-200'
                      : 'text-slate-700 hover:bg-slate-50 hover:text-slate-900'
                  }`}
                >
                  <div className="flex items-center gap-2.5">
                    <span className="text-lg leading-none">{meta.icon}</span>
                    <div>
                      <div className="font-semibold text-slate-900 flex items-center gap-1.5">
                        {meta.label}
                        {isSelected && (
                          <span className="w-1.5 h-1.5 rounded-full bg-blue-600 inline-block"></span>
                        )}
                      </div>
                      <div className="text-[10px] text-slate-500 font-normal line-clamp-1">
                        {meta.description}
                      </div>
                    </div>
                  </div>
                  <span
                    className={`ml-2 px-2 py-0.5 rounded-full text-[10px] font-mono font-bold flex-shrink-0 ${
                      isSelected
                        ? 'bg-blue-600 text-white'
                        : 'bg-slate-100 text-slate-600'
                    }`}
                  >
                    {count}
                  </span>
                </button>
              );
            })}
          </div>
        </div>
      )}
    </div>
  );
};
