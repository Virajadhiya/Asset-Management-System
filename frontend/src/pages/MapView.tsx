import React, { useState } from 'react';
import { MapContainer, TileLayer, Marker, Popup } from 'react-leaflet';
import 'leaflet/dist/leaflet.css';
import { useQuery } from '@tanstack/react-query';
import { api } from '../api/endpoints';
import { useAsset, ASSET_DEFINITIONS, AssetType } from '../context/AssetContext';
import { Link } from 'react-router-dom';
import L from 'leaflet';
import { ConditionBadge } from '../components/common/ConditionBadge';
import { StatusBadge } from '../components/common/StatusBadge';

// Helper to create colored SVG markers with asset iconography
const createMultiAssetMarkerIcon = (condition: string | null, assetType: string | undefined) => {
  let ringColor = '#3b82f6';
  if (condition === 'EXCELLENT') ringColor = '#16a34a';
  else if (condition === 'GOOD') ringColor = '#2563eb';
  else if (condition === 'FAIR') ringColor = '#eab308';
  else if (condition === 'POOR') ringColor = '#ea580c';
  else if (condition === 'CRITICAL') ringColor = '#dc2626';

  const type = (assetType || 'BRIDGE').toUpperCase();
  let emoji = '🌉';
  let badgeColor = '#2563eb';
  if (type === 'TUNNEL') { emoji = '🚇'; badgeColor = '#9333ea'; }
  else if (type === 'HIGHWAY') { emoji = '🛣️'; badgeColor = '#d97706'; }
  else if (type === 'CULVERT') { emoji = '📦'; badgeColor = '#059669'; }

  const html = `
    <div style="position: relative; width: 34px; height: 46px; cursor: pointer;">
      <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 36" width="34" height="46">
        <path d="M12 0C5.373 0 0 5.373 0 12c0 9 12 24 12 24s12-15 12-24c0-6.627-5.373-12-12-12z" fill="${badgeColor}" stroke="${ringColor}" stroke-width="2.5"/>
        <circle cx="12" cy="12" r="7.5" fill="#ffffff"/>
      </svg>
      <div style="position: absolute; top: 4px; left: 0; width: 34px; text-align: center; font-size: 11px; line-height: 16px; pointer-events: none;">
        ${emoji}
      </div>
    </div>
  `;

  return L.divIcon({
    html,
    className: 'custom-multi-asset-pin',
    iconSize: [34, 46],
    iconAnchor: [17, 46],
    popupAnchor: [0, -42],
  });
};

export default function MapView() {
  const { activeAssetType, setAssetType, activeMeta, getMeta } = useAsset();
  const [selectedCondition, setSelectedCondition] = useState<string>('ALL');
  const [selectedStatus, setSelectedStatus] = useState<string>('ALL');
  const [assetTypeFilter, setAssetTypeFilter] = useState<string>(activeAssetType);

  const { data: rawBridges = [], isLoading, isError, refetch } = useQuery({
    queryKey: ['gis-bridges', assetTypeFilter],
    queryFn: () => api.getGISBridges({
      asset_type: assetTypeFilter !== 'ALL' ? assetTypeFilter : undefined,
    }),
  });

  const bridges: any[] = Array.isArray(rawBridges)
    ? rawBridges
    : (rawBridges?.items || rawBridges?.bridges || []);

  const filteredBridges = bridges.filter((b: any) => {
    if (selectedCondition !== 'ALL' && b.condition_category !== selectedCondition) return false;
    if (selectedStatus !== 'ALL' && b.current_status !== selectedStatus) return false;
    return true;
  });

  if (isLoading) return <div className="p-8 text-center text-slate-500">Loading GIS spatial data...</div>;

  if (isError) {
    return (
      <div className="p-8 bg-white rounded-lg border border-red-200 text-center space-y-3">
        <h3 className="text-base font-bold text-red-600">Failed to load GIS spatial coordinates</h3>
        <p className="text-xs text-slate-500">Unable to reach the GIS service or session has expired.</p>
        <button
          onClick={() => refetch()}
          className="px-4 py-2 bg-blue-600 text-white rounded text-xs font-semibold hover:bg-blue-700"
        >
          Retry Loading
        </button>
      </div>
    );
  }

  return (
    <div className="space-y-4">
      {/* Controls & Filter Bar */}
      <div className="bg-white p-4 rounded-lg shadow-sm border border-slate-200 flex flex-wrap justify-between items-center gap-4">
        <div>
          <h2 className="text-base font-bold text-slate-900 flex items-center gap-2">
            <span>GIS Multi-Asset Spatial Map</span>
            <span className="text-xs px-2 py-0.5 rounded-full bg-slate-100 text-slate-600 font-mono font-bold">
              {filteredBridges.length} / {bridges.length} assets
            </span>
          </h2>
          <p className="text-xs text-slate-500">
            Interactive geospatial mapping of Gujarat infrastructure: bridges, tunnels, expressways, and culverts.
          </p>
        </div>

        <div className="flex items-center gap-3 flex-wrap">
          {/* Asset Type Layer Selector */}
          <div>
            <label className="block text-[10px] text-slate-400 uppercase font-bold mb-0.5">Asset Layer</label>
            <select
              value={assetTypeFilter}
              onChange={e => {
                setAssetTypeFilter(e.target.value);
                setAssetType(e.target.value as AssetType);
              }}
              className="px-2.5 py-1.5 border border-slate-300 rounded text-xs bg-white text-slate-800 font-semibold"
            >
              <option value="ALL">🌐 All Infrastructure (45)</option>
              <option value="BRIDGE">🌉 Bridges (30)</option>
              <option value="TUNNEL">🚇 Tunnels (5)</option>
              <option value="HIGHWAY">🛣️ Highways (5)</option>
              <option value="CULVERT">📦 Culverts (5)</option>
            </select>
          </div>

          <div>
            <label className="block text-[10px] text-slate-400 uppercase font-bold mb-0.5">Condition</label>
            <select
              value={selectedCondition}
              onChange={e => setSelectedCondition(e.target.value)}
              className="px-2.5 py-1.5 border border-slate-300 rounded text-xs bg-white text-slate-700"
            >
              <option value="ALL">All Conditions</option>
              <option value="EXCELLENT">Excellent</option>
              <option value="GOOD">Good</option>
              <option value="FAIR">Fair</option>
              <option value="POOR">Poor</option>
              <option value="CRITICAL">Critical</option>
            </select>
          </div>

          <div>
            <label className="block text-[10px] text-slate-400 uppercase font-bold mb-0.5">Status</label>
            <select
              value={selectedStatus}
              onChange={e => setSelectedStatus(e.target.value)}
              className="px-2.5 py-1.5 border border-slate-300 rounded text-xs bg-white text-slate-700"
            >
              <option value="ALL">All Statuses</option>
              <option value="OPERATIONAL">Operational</option>
              <option value="UNDER_MAINTENANCE">Under Maintenance</option>
              <option value="UNDER_REHABILITATION">Under Rehabilitation</option>
              <option value="CLOSED">Closed</option>
              <option value="UNDER_CONSTRUCTION">Under Construction</option>
              <option value="PLANNED">Planned</option>
            </select>
          </div>
        </div>
      </div>

      {/* Map Container */}
      <div className="h-[calc(100vh-230px)] w-full rounded-lg overflow-hidden border border-slate-200 shadow-sm relative z-0">
        <MapContainer center={[22.4, 71.9]} zoom={7.5} style={{ height: '100%', width: '100%' }}>
          <TileLayer
            attribution='&copy; OpenStreetMap contributors, MoRTH IBMS'
            url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
          />
          {filteredBridges.map((bridge: any) => {
            const bId = bridge.bridge_id || bridge.id;
            const bName = bridge.bridge_name || bridge.name || 'Asset';
            const bCode = bridge.bridge_code || bridge.bridge_id_str || 'ID';
            const aType = bridge.asset_type || 'BRIDGE';
            const meta = getMeta(aType);
            const lat = bridge.latitude || 22.0;
            const lng = bridge.longitude || 71.0;
            const bStatus = bridge.current_status || bridge.status || 'OPERATIONAL';
            const bCond = bridge.condition_category || bridge.condition || null;
            const bHealth = bridge.health_index ?? null;

            return (
              <Marker
                key={bId}
                position={[lat, lng]}
                icon={createMultiAssetMarkerIcon(bCond, aType)}
              >
                <Popup>
                  <div className="p-1 min-w-[220px]">
                    <div className="flex items-center gap-1.5 mb-1">
                      <span className="text-base">{meta.icon}</span>
                      <span className={`px-1.5 py-0.2 rounded text-[10px] font-bold ${meta.badgeBg} ${meta.badgeText}`}>
                        {meta.singular}
                      </span>
                    </div>
                    <div className="font-bold text-sm text-slate-900 leading-snug">{bName}</div>
                    <div className="text-[11px] font-mono font-semibold text-slate-500 mb-2">{bCode}</div>
                    
                    <div className="space-y-1.5 text-xs border-t border-slate-100 pt-2">
                      <div className="flex justify-between items-center">
                        <span className="text-slate-400">District:</span>
                        <span className="font-medium text-slate-700">{bridge.district || 'Gujarat'}</span>
                      </div>
                      <div className="flex justify-between items-center">
                        <span className="text-slate-400">Status:</span>
                        <StatusBadge status={bStatus} />
                      </div>
                      <div className="flex justify-between items-center">
                        <span className="text-slate-400">Condition:</span>
                        <ConditionBadge condition={bCond} />
                      </div>
                      {bHealth != null && (
                        <div className="flex justify-between items-center pt-1 border-t border-slate-100">
                          <span className="font-semibold text-slate-600">{meta.healthShort}:</span>
                          <span className="font-black text-blue-600 text-sm">{bHealth} / 100</span>
                        </div>
                      )}
                    </div>

                    <div className="mt-3 pt-2 border-t border-slate-100 text-right">
                      <Link
                        to={`/bridges/${bId}`}
                        className="inline-block text-xs font-bold text-blue-600 hover:text-blue-800"
                      >
                        Inspect Full Asset &rarr;
                      </Link>
                    </div>
                  </div>
                </Popup>
              </Marker>
            );
          })}
        </MapContainer>
      </div>

      {/* Map Legend */}
      <div className="bg-white px-4 py-2.5 rounded-lg shadow-sm border border-slate-200 flex items-center justify-between text-xs text-slate-600 flex-wrap gap-3">
        <div className="flex items-center gap-3 flex-wrap">
          <span className="font-bold text-slate-800">Asset Symbols:</span>
          <span className="flex items-center gap-1">🌉 Bridges</span>
          <span className="flex items-center gap-1">🚇 Tunnels</span>
          <span className="flex items-center gap-1">🛣️ Highways</span>
          <span className="flex items-center gap-1">📦 Culverts</span>
        </div>

        <div className="flex items-center gap-3 flex-wrap border-l border-slate-200 pl-3">
          <span className="font-bold text-slate-800">Condition Rings:</span>
          <span className="flex items-center gap-1"><span className="w-2.5 h-2.5 rounded-full bg-emerald-600 inline-block" /> Excellent</span>
          <span className="flex items-center gap-1"><span className="w-2.5 h-2.5 rounded-full bg-blue-600 inline-block" /> Good</span>
          <span className="flex items-center gap-1"><span className="w-2.5 h-2.5 rounded-full bg-amber-500 inline-block" /> Fair</span>
          <span className="flex items-center gap-1"><span className="w-2.5 h-2.5 rounded-full bg-orange-600 inline-block" /> Poor</span>
          <span className="flex items-center gap-1"><span className="w-2.5 h-2.5 rounded-full bg-red-600 inline-block" /> Critical</span>
        </div>
      </div>
    </div>
  );
}