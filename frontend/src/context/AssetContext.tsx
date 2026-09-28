import React, { createContext, useContext, useState, useEffect } from 'react';

export type AssetType = 'ALL' | 'BRIDGE' | 'TUNNEL' | 'HIGHWAY' | 'CULVERT';

export interface AssetMeta {
  type: AssetType;
  label: string;
  plural: string;
  singular: string;
  icon: string;
  color: string;
  badgeBg: string;
  badgeText: string;
  healthMetric: string;
  healthShort: string;
  description: string;
}

export const ASSET_DEFINITIONS: Record<AssetType, AssetMeta> = {
  ALL: {
    type: 'ALL',
    label: 'All Infrastructure',
    plural: 'Infrastructure Portfolio',
    singular: 'Infrastructure Asset',
    icon: '🌐',
    color: '#0f172a',
    badgeBg: 'bg-slate-900',
    badgeText: 'text-white',
    healthMetric: 'Portfolio Health Index',
    healthShort: 'PHI',
    description: 'Unified cross-asset executive portfolio across Gujarat',
  },
  BRIDGE: {
    type: 'BRIDGE',
    label: 'Bridges',
    plural: 'Bridge Registry',
    singular: 'Bridge',
    icon: '🌉',
    color: '#2563eb',
    badgeBg: 'bg-blue-600',
    badgeText: 'text-white',
    healthMetric: 'Bridge Health Index (BHI)',
    healthShort: 'BHI',
    description: 'Major, minor, arch, truss, and cable-stayed river & valley crossings',
  },
  TUNNEL: {
    type: 'TUNNEL',
    label: 'Tunnels',
    plural: 'Tunnel Registry',
    singular: 'Tunnel',
    icon: '🚇',
    color: '#9333ea',
    badgeBg: 'bg-purple-600',
    badgeText: 'text-white',
    healthMetric: 'Tunnel Health Index (THI)',
    healthShort: 'THI',
    description: 'Subterranean transit, mountain tunnels, and coastal underpasses',
  },
  HIGHWAY: {
    type: 'HIGHWAY',
    label: 'Highways & Pavements',
    plural: 'Highway Registry',
    singular: 'Highway Stretch',
    icon: '🛣️',
    color: '#d97706',
    badgeBg: 'bg-amber-600',
    badgeText: 'text-white',
    healthMetric: 'Pavement Condition Index (PCI)',
    healthShort: 'PCI',
    description: 'Expressways, National Highways, and state arterial road corridors',
  },
  CULVERT: {
    type: 'CULVERT',
    label: 'Culverts & Drains',
    plural: 'Culvert Registry',
    singular: 'Culvert',
    icon: '📦',
    color: '#059669',
    badgeBg: 'bg-emerald-600',
    badgeText: 'text-white',
    healthMetric: 'Culvert Health Index (CHI)',
    healthShort: 'CHI',
    description: 'Cross-drainage box, pipe, and flood relief hydraulic structures',
  },
};

interface AssetContextType {
  activeAssetType: AssetType;
  setAssetType: (type: AssetType) => void;
  activeMeta: AssetMeta;
  getMeta: (type: string | undefined) => AssetMeta;
}

const AssetContext = createContext<AssetContextType | undefined>(undefined);

const STORAGE_KEY = 'pravi_active_asset_type';

export function AssetProvider({ children }: { children: React.ReactNode }) {
  const [activeAssetType, setActiveAssetTypeState] = useState<AssetType>(() => {
    const saved = localStorage.getItem(STORAGE_KEY) as AssetType;
    return saved && ASSET_DEFINITIONS[saved] ? saved : 'ALL';
  });

  const setAssetType = (type: AssetType) => {
    setActiveAssetTypeState(type);
    localStorage.setItem(STORAGE_KEY, type);
  };

  const activeMeta = ASSET_DEFINITIONS[activeAssetType];

  const getMeta = (type: string | undefined): AssetMeta => {
    if (!type) return ASSET_DEFINITIONS.BRIDGE;
    const normalized = type.toUpperCase() as AssetType;
    return ASSET_DEFINITIONS[normalized] || ASSET_DEFINITIONS.BRIDGE;
  };

  return (
    <AssetContext.Provider value={{ activeAssetType, setAssetType, activeMeta, getMeta }}>
      {children}
    </AssetContext.Provider>
  );
}

export function useAsset() {
  const context = useContext(AssetContext);
  if (!context) {
    throw new Error('useAsset must be used within an AssetProvider');
  }
  return context;
}
