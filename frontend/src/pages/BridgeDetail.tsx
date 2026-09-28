import React, { useState } from 'react';
import { useParams, Link, useNavigate } from 'react-router-dom';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { api } from '../api/endpoints';
import { StatusBadge } from '../components/common/StatusBadge';
import { ConditionBadge } from '../components/common/ConditionBadge';
import { PriorityBadge } from '../components/common/PriorityBadge';
import { useAuth } from '../context/AuthContext';
import { useAsset } from '../context/AssetContext';

export default function BridgeDetail() {
  const { id } = useParams<{ id: string }>();
  const { getMeta } = useAsset();
  const [activeTab, setActiveTab] = useState('overview');
  const [expandedInspection, setExpandedInspection] = useState<string | null>(null);
  const [showMaintModal, setShowMaintModal] = useState(false);
  const [showLifecycleModal, setShowLifecycleModal] = useState(false);
  const [showDeleteModal, setShowDeleteModal] = useState(false);
  const navigate = useNavigate();
  const { user, hasPermission } = useAuth();
  const queryClient = useQueryClient();

  // New Maintenance form state
  const [maintType, setMaintType] = useState('REPAIR');
  const [maintPriority, setMaintPriority] = useState('HIGH');
  const [maintDesc, setMaintDesc] = useState('');
  const [maintCost, setMaintCost] = useState('250000');

  // Procurement Lifecycle Actions Modal State
  const [procurementModal, setProcurementModal] = useState<{
    maint: any;
    action: 'estimate' | 'sanction' | 'award_tender' | 'complete' | 'verify';
  } | null>(null);

  const [procEstimateCost, setProcEstimateCost] = useState('350000');
  const [procSanctionNo, setProcSanctionNo] = useState('AA/PWD/2026/042');
  const [procSanctionedAmt, setProcSanctionedAmt] = useState('350000');
  const [procTenderNo, setProcTenderNo] = useState('NIT/NHAI/2026/089');
  const [procWorkOrderNo, setProcWorkOrderNo] = useState('WO-PWD-8421');
  const [procTenderVal, setProcTenderVal] = useState('342000');
  const [procContractor, setProcContractor] = useState('Larsen & Toubro Ltd.');
  const [procActualCost, setProcActualCost] = useState('338500');
  const [procRemarks, setProcRemarks] = useState('');

  // Counter-Sign Inspection Modal State
  const [counterSignInsp, setCounterSignInsp] = useState<any | null>(null);
  const [counterSignRemarks, setCounterSignRemarks] = useState('');

  // Report Distress Modal State
  const [showReportIssueModal, setShowReportIssueModal] = useState(false);
  const [issueSource, setIssueSource] = useState('CITIZEN_REPORT');
  const [issueType, setIssueType] = useState('STRUCTURAL_CRACK');
  const [issueSeverity, setIssueSeverity] = useState('HIGH');
  const [issueDesc, setIssueDesc] = useState('');
  const [issueLocation, setIssueLocation] = useState('');
  const [issuePhoto, setIssuePhoto] = useState('https://images.unsplash.com/photo-1545558014-8692077e9b5c?auto=format&fit=crop&w=800&q=80');

  // New Lifecycle Event form state
  const [lifecycleType, setLifecycleType] = useState('MAINTENANCE_STARTED');
  const [lifecycleDesc, setLifecycleDesc] = useState('');

  // Queries
  const { data: bridge, isLoading: loadingBridge } = useQuery({
    queryKey: ['bridge', id],
    queryFn: () => api.getBridge(id!),
  });

  const { data: inspections = [], isLoading: loadingInspections } = useQuery({
    queryKey: ['bridge-inspections', id],
    queryFn: () => api.getBridgeInspections(id!),
    enabled: activeTab === 'inspections',
  });

  const { data: maintenanceRecords = [], isLoading: loadingMaint } = useQuery({
    queryKey: ['bridge-maintenance', id],
    queryFn: () => api.getBridgeMaintenance(id!),
    enabled: activeTab === 'maintenance',
  });

  const { data: bridgeIssues = [], isLoading: loadingIssues } = useQuery({
    queryKey: ['bridge-issues', id],
    queryFn: () => api.getBridgeIssues(id!),
    enabled: activeTab === 'issues',
  });

  const { data: lifecycleEvents = [], isLoading: loadingLifecycle } = useQuery({
    queryKey: ['bridge-lifecycle', id],
    queryFn: () => api.getBridgeLifecycle(id!),
    enabled: activeTab === 'lifecycle',
  });

  // Mutations
  const updateMaintStatusMutation = useMutation({
    mutationFn: (payload: {
      maintId: string;
      action: string;
      remarks?: string;
      estimated_cost?: number;
      sanction_number?: string;
      sanctioned_amount?: number;
      tender_number?: string;
      work_order_number?: string;
      tender_value?: number;
      assigned_contractor?: string;
      actual_cost?: number;
    }) => api.updateMaintenanceStatus(payload.maintId, payload),
    onSuccess: () => {
      setProcurementModal(null);
      setProcRemarks('');
      queryClient.invalidateQueries({ queryKey: ['bridge-maintenance', id] });
      queryClient.invalidateQueries({ queryKey: ['bridge', id] });
      queryClient.invalidateQueries({ queryKey: ['bridge-lifecycle', id] });
    },
  });

  const counterSignMutation = useMutation({
    mutationFn: ({ inspId, remarks }: { inspId: string; remarks?: string }) =>
      api.counterSignInspection(inspId, remarks),
    onSuccess: () => {
      setCounterSignInsp(null);
      setCounterSignRemarks('');
      queryClient.invalidateQueries({ queryKey: ['bridge-inspections', id] });
      queryClient.invalidateQueries({ queryKey: ['bridge', id] });
    },
  });

  const createBridgeIssueMutation = useMutation({
    mutationFn: (payload: any) => api.createIssue(payload),
    onSuccess: () => {
      setShowReportIssueModal(false);
      setIssueDesc('');
      setIssueLocation('');
      queryClient.invalidateQueries({ queryKey: ['bridge-issues', id] });
      queryClient.invalidateQueries({ queryKey: ['issues'] });
    },
  });

  const createMaintMutation = useMutation({
    mutationFn: (payload: any) => api.createMaintenance(id!, payload),
    onSuccess: () => {
      setShowMaintModal(false);
      setMaintDesc('');
      queryClient.invalidateQueries({ queryKey: ['bridge-maintenance', id] });
      queryClient.invalidateQueries({ queryKey: ['bridge', id] });
    },
  });

  const createLifecycleMutation = useMutation({
    mutationFn: (payload: any) => api.createLifecycleEvent(id!, payload),
    onSuccess: () => {
      setShowLifecycleModal(false);
      setLifecycleDesc('');
      queryClient.invalidateQueries({ queryKey: ['bridge-lifecycle', id] });
      queryClient.invalidateQueries({ queryKey: ['bridge', id] });
    },
  });

  const deleteMutation = useMutation({
    mutationFn: () => api.deleteBridge(id!),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['bridges'] });
      queryClient.invalidateQueries({ queryKey: ['dashboard-summary'] });
      queryClient.invalidateQueries({ queryKey: ['gis-bridges'] });
      navigate('/bridges');
    },
  });

  if (loadingBridge) return <div className="p-8 text-center text-slate-500">Loading asset details...</div>;
  if (!bridge) return <div className="p-8 text-center text-red-500">Asset not found.</div>;

  const tabs = [
    { id: 'overview', label: 'Overview' },
    { id: 'engineering', label: 'Engineering' },
    { id: 'condition', label: 'Health & Condition' },
    { id: 'issues', label: 'Distress Issues' },
    { id: 'inspections', label: 'Inspections & Audit' },
    { id: 'maintenance', label: 'Procurement & Maintenance' },
    { id: 'lifecycle', label: 'Lifecycle Timeline' },
  ];

  const handleCreateMaintenance = (e: React.FormEvent) => {
    e.preventDefault();
    createMaintMutation.mutate({
      maintenance_type: maintType,
      priority: maintPriority,
      description: maintDesc,
      estimated_cost: parseFloat(maintCost) || 0,
    });
  };

  const handleCreateLifecycle = (e: React.FormEvent) => {
    e.preventDefault();
    createLifecycleMutation.mutate({
      event_type: lifecycleType,
      event_date: new Date().toISOString().split('T')[0],
      description: lifecycleDesc || `Transition to ${lifecycleType}`,
    });
  };

  const handleProcurementSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!procurementModal) return;
    const { maint, action } = procurementModal;

    const payload: any = {
      maintId: maint.maintenance_id,
      action,
      remarks: procRemarks,
    };

    if (action === 'estimate') {
      payload.estimated_cost = parseFloat(procEstimateCost) || 0;
    } else if (action === 'sanction') {
      payload.sanction_number = procSanctionNo;
      payload.sanctioned_amount = parseFloat(procSanctionedAmt) || 0;
    } else if (action === 'award_tender') {
      payload.tender_number = procTenderNo;
      payload.work_order_number = procWorkOrderNo;
      payload.tender_value = parseFloat(procTenderVal) || 0;
      payload.assigned_contractor = procContractor;
    } else if (action === 'complete') {
      payload.actual_cost = parseFloat(procActualCost) || 0;
    }

    updateMaintStatusMutation.mutate(payload);
  };

  const isEngineer = ['EXECUTIVE_ENGINEER', 'ADMIN'].includes(user?.role || '');
  const isDeptHead = ['DEPARTMENT_HEAD', 'ADMIN'].includes(user?.role || '');
  const isMaintenanceOfficer = ['MAINTENANCE_OFFICER', 'EXECUTIVE_ENGINEER', 'ADMIN'].includes(user?.role || '');

  return (
    <div className="max-w-7xl mx-auto space-y-6 pb-12">
      {/* Header Banner */}
      {(() => {
        const meta = getMeta(bridge.asset_type);
        return (
          <div className="bg-white p-6 rounded-lg shadow-sm border border-slate-200 flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
            <div>
              <div className="flex items-center gap-3 mb-2 flex-wrap">
                <span className="text-2xl">{meta.icon}</span>
                <h1 className="text-2xl font-bold text-slate-900">{bridge.bridge_name}</h1>
                <span className="px-2.5 py-0.5 bg-slate-100 text-slate-700 rounded text-xs font-mono font-semibold border border-slate-300">
                  {bridge.bridge_code}
                </span>
                <span className={`px-2 py-0.5 rounded text-[11px] font-bold ${meta.badgeBg} ${meta.badgeText}`}>
                  {meta.singular}
                </span>
              </div>
              <div className="flex items-center gap-3 text-xs text-slate-500 flex-wrap">
                <span>{bridge.location?.district}, {bridge.location?.state}</span>
                <span>&bull;</span>
                <span className="font-medium text-slate-700">
                  {bridge.owning_authority || 'NHAI'} ({bridge.department || 'MoRTH'})
                </span>
                <span>&bull;</span>
                <span>Constructed: {bridge.year_constructed || 'N/A'}</span>
                <span>&bull;</span>
                <span>Road: {bridge.road_name || 'National Highway'}</span>
              </div>
            </div>

            <div className="flex items-center gap-3 flex-wrap">
              <StatusBadge status={bridge.current_status} />
              <ConditionBadge condition={bridge.latest_condition?.condition_category || 'GOOD'} />
              <div className="flex items-center gap-1.5 px-3 py-1 bg-blue-50 border border-blue-200 rounded-md">
                <span className="text-xs text-blue-700 font-medium">BHI:</span>
                <span className="text-sm font-bold text-blue-900">
                  {bridge.latest_condition?.overall_health_index ?? 78}/100
                </span>
              </div>

              {/* Administrative Delete Asset */}
              {user?.role === 'ADMIN' && (
                <button
                  onClick={() => setShowDeleteModal(true)}
                  className="px-2.5 py-1 text-xs font-semibold text-red-600 hover:text-red-800 hover:bg-red-50 rounded border border-red-200 transition-colors ml-2"
                >
                  Delete Asset
                </button>
              )}
            </div>
          </div>
        );
      })()}

      {/* Navigation Tabs */}
      <div className="flex border-b border-slate-200 gap-1 bg-white px-4 rounded-lg shadow-xs overflow-x-auto">
        {tabs.map(tab => (
          <button
            key={tab.id}
            onClick={() => setActiveTab(tab.id)}
            className={`py-3 px-4 text-xs font-semibold whitespace-nowrap border-b-2 transition-colors ${
              activeTab === tab.id
                ? 'border-blue-600 text-blue-600'
                : 'border-transparent text-slate-500 hover:text-slate-700'
            }`}
          >
            {tab.label}
          </button>
        ))}
      </div>

      {/* Tab Panels */}
      <div>
        {/* Tab 1: Overview */}
        {activeTab === 'overview' && (
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <div className="md:col-span-2 space-y-6">
              <div className="bg-white p-6 rounded-lg shadow-sm border border-slate-200">
                <h3 className="text-base font-semibold text-slate-900 border-b border-slate-100 pb-3 mb-4">
                  Asset Summary & Traffic Profile
                </h3>
                <div className="grid grid-cols-2 sm:grid-cols-3 gap-4 text-xs">
                  <div>
                    <span className="text-slate-400 block font-medium">Structure Type</span>
                    <span className="font-semibold text-slate-800 text-sm mt-0.5 block">{bridge.bridge_type}</span>
                  </div>
                  <div>
                    <span className="text-slate-400 block font-medium">Category</span>
                    <span className="font-semibold text-slate-800 text-sm mt-0.5 block">{bridge.structure_category}</span>
                  </div>
                  <div>
                    <span className="text-slate-400 block font-medium">Traffic Status</span>
                    <span className="font-semibold text-slate-800 text-sm mt-0.5 block">{bridge.traffic_status || 'Normal Flow'}</span>
                  </div>
                  <div>
                    <span className="text-slate-400 block font-medium">Daily Traffic (PCU)</span>
                    <span className="font-semibold text-slate-800 text-sm mt-0.5 block">
                      {bridge.daily_traffic_estimate ? `${bridge.daily_traffic_estimate.toLocaleString()} vpd` : 'N/A'}
                    </span>
                  </div>
                  <div>
                    <span className="text-slate-400 block font-medium">Load Restriction</span>
                    <span className="font-semibold text-slate-800 text-sm mt-0.5 block">{bridge.load_restriction || 'None (Class 70R)'}</span>
                  </div>
                  <div>
                    <span className="text-slate-400 block font-medium">Speed Limit</span>
                    <span className="font-semibold text-slate-800 text-sm mt-0.5 block">{bridge.speed_restriction ? `${bridge.speed_restriction} km/h` : 'Standard'}</span>
                  </div>
                </div>

                {bridge.description && (
                  <div className="mt-4 pt-4 border-t border-slate-100 text-xs text-slate-600">
                    <span className="font-semibold text-slate-700">Description: </span>
                    {bridge.description}
                  </div>
                )}
              </div>

              {/* Location Details */}
              <div className="bg-white p-6 rounded-lg shadow-sm border border-slate-200">
                <h3 className="text-base font-semibold text-slate-900 border-b border-slate-100 pb-3 mb-4">
                  Spatial Location & Route Chainage
                </h3>
                <div className="grid grid-cols-2 sm:grid-cols-3 gap-4 text-xs">
                  <div>
                    <span className="text-slate-400 block font-medium">State / UT</span>
                    <span className="font-semibold text-slate-800 mt-0.5 block">{bridge.location?.state}</span>
                  </div>
                  <div>
                    <span className="text-slate-400 block font-medium">District</span>
                    <span className="font-semibold text-slate-800 mt-0.5 block">{bridge.location?.district}</span>
                  </div>
                  <div>
                    <span className="text-slate-400 block font-medium">Taluka / Tehsil</span>
                    <span className="font-semibold text-slate-800 mt-0.5 block">{bridge.location?.taluka || 'Headquarters'}</span>
                  </div>
                  <div>
                    <span className="text-slate-400 block font-medium">GPS Latitude</span>
                    <span className="font-mono text-slate-800 mt-0.5 block">{bridge.location?.latitude?.toFixed(4)}° N</span>
                  </div>
                  <div>
                    <span className="text-slate-400 block font-medium">GPS Longitude</span>
                    <span className="font-mono text-slate-800 mt-0.5 block">{bridge.location?.longitude?.toFixed(4)}° E</span>
                  </div>
                  <div>
                    <span className="text-slate-400 block font-medium">Elevation</span>
                    <span className="font-semibold text-slate-800 mt-0.5 block">{bridge.location?.elevation ? `${bridge.location.elevation} m MSL` : '42 m MSL'}</span>
                  </div>
                </div>
              </div>
            </div>

            {/* Right Column: Key Status Cards */}
            <div className="space-y-6">
              <div className="bg-white p-5 rounded-lg shadow-sm border border-slate-200">
                <h4 className="text-xs font-bold text-slate-400 uppercase tracking-wider mb-3">Asset Health Index</h4>
                <div className="flex items-baseline gap-2">
                  <span className="text-4xl font-black text-slate-900">{bridge.latest_condition?.overall_health_index ?? 78}</span>
                  <span className="text-sm font-semibold text-slate-500">/ 100</span>
                </div>
                <div className="mt-2 text-xs text-slate-600">
                  Category: <span className="font-bold text-slate-800">{bridge.latest_condition?.condition_category || 'GOOD'}</span>
                </div>
                <div className="w-full bg-slate-100 h-2 rounded-full mt-3 overflow-hidden">
                  <div
                    className={`h-full rounded-full ${
                      (bridge.latest_condition?.overall_health_index ?? 78) >= 80 ? 'bg-emerald-500' :
                      (bridge.latest_condition?.overall_health_index ?? 78) >= 60 ? 'bg-amber-500' : 'bg-red-500'
                    }`}
                    style={{ width: `${bridge.latest_condition?.overall_health_index ?? 78}%` }}
                  />
                </div>
                <div className="mt-4 pt-3 border-t border-slate-100 flex justify-between items-center text-xs text-slate-500">
                  <span>Last Assessment:</span>
                  <span className="font-medium text-slate-700">{bridge.latest_condition?.assessment_date || '2026-03-15'}</span>
                </div>
              </div>

              {/* Maintenance Quick Status */}
              <div className="bg-white p-5 rounded-lg shadow-sm border border-slate-200">
                <h4 className="text-xs font-bold text-slate-400 uppercase tracking-wider mb-2">Procurement Status</h4>
                <div className="text-sm font-bold text-slate-800">
                  {bridge.current_status === 'UNDER_MAINTENANCE' ? 'Active Work In Progress' : 'Operational / Normal'}
                </div>
                <p className="text-xs text-slate-500 mt-1">
                  Managing Authority: <span className="font-semibold text-slate-700">{bridge.maintaining_authority || 'PWD Roads Division'}</span>
                </p>
                <div className="mt-4">
                  <button
                    onClick={() => setActiveTab('maintenance')}
                    className="w-full py-1.5 bg-blue-50 hover:bg-blue-100 text-blue-700 rounded text-xs font-semibold transition-colors"
                  >
                    View Procurement Pipeline &rarr;
                  </button>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Tab 2: Engineering Specs */}
        {activeTab === 'engineering' && (
          <div className="bg-white p-6 rounded-lg shadow-sm border border-slate-200 space-y-6">
            <h3 className="text-base font-semibold text-slate-900 border-b border-slate-100 pb-3">
              Engineering & Structural Specifications
            </h3>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-xs">
              <div className="p-3 bg-slate-50 rounded">
                <span className="text-slate-400 block font-medium">Total Length</span>
                <span className="font-bold text-slate-800 text-sm mt-0.5 block">{bridge.engineering?.total_length ? `${bridge.engineering.total_length} m` : '240 m'}</span>
              </div>
              <div className="p-3 bg-slate-50 rounded">
                <span className="text-slate-400 block font-medium">Carriageway Width</span>
                <span className="font-bold text-slate-800 text-sm mt-0.5 block">{bridge.engineering?.carriageway_width ? `${bridge.engineering.carriageway_width} m` : '10.5 m'}</span>
              </div>
              <div className="p-3 bg-slate-50 rounded">
                <span className="text-slate-400 block font-medium">Number of Spans</span>
                <span className="font-bold text-slate-800 text-sm mt-0.5 block">{bridge.engineering?.number_of_spans ?? 6}</span>
              </div>
              <div className="p-3 bg-slate-50 rounded">
                <span className="text-slate-400 block font-medium">Number of Lanes</span>
                <span className="font-bold text-slate-800 text-sm mt-0.5 block">{bridge.engineering?.number_of_lanes ?? 4} Lanes</span>
              </div>
              <div className="p-3 bg-slate-50 rounded">
                <span className="text-slate-400 block font-medium">Superstructure</span>
                <span className="font-bold text-slate-800 text-sm mt-0.5 block">{bridge.engineering?.superstructure_type || 'Prestressed Concrete Box Girder'}</span>
              </div>
              <div className="p-3 bg-slate-50 rounded">
                <span className="text-slate-400 block font-medium">Substructure</span>
                <span className="font-bold text-slate-800 text-sm mt-0.5 block">{bridge.engineering?.substructure_type || 'RCC Circular Piers'}</span>
              </div>
              <div className="p-3 bg-slate-50 rounded">
                <span className="text-slate-400 block font-medium">Foundation</span>
                <span className="font-bold text-slate-800 text-sm mt-0.5 block">{bridge.engineering?.foundation_type || 'Well Foundation'}</span>
              </div>
              <div className="p-3 bg-slate-50 rounded">
                <span className="text-slate-400 block font-medium">Design Life</span>
                <span className="font-bold text-slate-800 text-sm mt-0.5 block">{bridge.engineering?.design_life ? `${bridge.engineering.design_life} Years` : '100 Years'}</span>
              </div>
            </div>
          </div>
        )}

        {/* Tab 3: Health & Condition */}
        {activeTab === 'condition' && (
          <div className="bg-white p-6 rounded-lg shadow-sm border border-slate-200 space-y-6">
            <h3 className="text-base font-semibold text-slate-900 border-b border-slate-100 pb-3">
              Health Index Score Breakdown
            </h3>
            <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
              <div className="p-4 bg-slate-50 rounded-lg border border-slate-100">
                <div className="text-xs text-slate-500 font-semibold">Structural Integrity (40%)</div>
                <div className="text-2xl font-bold text-slate-800 mt-1">{bridge.latest_condition?.structural_score ?? 75}%</div>
                <div className="w-full bg-slate-200 h-1.5 rounded-full mt-2 overflow-hidden">
                  <div className="bg-blue-600 h-full rounded-full" style={{ width: `${bridge.latest_condition?.structural_score ?? 75}%` }} />
                </div>
              </div>
              <div className="p-4 bg-slate-50 rounded-lg border border-slate-100">
                <div className="text-xs text-slate-500 font-semibold">Functional Capacity (30%)</div>
                <div className="text-2xl font-bold text-slate-800 mt-1">{bridge.latest_condition?.functional_score ?? 80}%</div>
                <div className="w-full bg-slate-200 h-1.5 rounded-full mt-2 overflow-hidden">
                  <div className="bg-emerald-600 h-full rounded-full" style={{ width: `${bridge.latest_condition?.functional_score ?? 80}%` }} />
                </div>
              </div>
              <div className="p-4 bg-slate-50 rounded-lg border border-slate-100">
                <div className="text-xs text-slate-500 font-semibold">Safety Score (20%)</div>
                <div className="text-2xl font-bold text-slate-800 mt-1">{bridge.latest_condition?.safety_score ?? 70}%</div>
                <div className="w-full bg-slate-200 h-1.5 rounded-full mt-2 overflow-hidden">
                  <div className="bg-amber-500 h-full rounded-full" style={{ width: `${bridge.latest_condition?.safety_score ?? 70}%` }} />
                </div>
              </div>
              <div className="p-4 bg-slate-50 rounded-lg border border-slate-100">
                <div className="text-xs text-slate-500 font-semibold">Age Remaining (10%)</div>
                <div className="text-2xl font-bold text-slate-800 mt-1">
                  {bridge.year_constructed ? Math.max(0, 100 - (2026 - bridge.year_constructed)) : 80}%
                </div>
                <div className="w-full bg-slate-200 h-1.5 rounded-full mt-2 overflow-hidden">
                  <div className="bg-indigo-600 h-full rounded-full" style={{ width: `${bridge.year_constructed ? Math.max(0, 100 - (2026 - bridge.year_constructed)) : 80}%` }} />
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Tab 4: Distress Issues */}
        {activeTab === 'issues' && (
          <div className="bg-white rounded-lg shadow-sm border border-slate-200 overflow-hidden">
            <div className="p-4 border-b border-slate-200 bg-slate-50 flex justify-between items-center">
              <div>
                <h3 className="text-base font-semibold text-slate-900">Distress Incidents & Task Allocation</h3>
                <p className="text-xs text-slate-500">Defects reported for this asset via field inspections, citizen alerts, or BHI alarms.</p>
              </div>
              <div className="flex items-center gap-2">
                <button
                  onClick={() => setShowReportIssueModal(true)}
                  className="px-3.5 py-1.5 bg-red-600 hover:bg-red-700 text-white rounded text-xs font-semibold shadow-xs flex items-center gap-1.5 transition-colors"
                >
                  <span>⚠️</span>
                  <span>Report Distress on this Asset</span>
                </button>
                <Link
                  to="/issues"
                  className="px-3 py-1.5 border border-slate-300 hover:bg-slate-50 text-slate-700 rounded text-xs font-semibold"
                >
                  View Global Registry
                </Link>
              </div>
            </div>

            {loadingIssues ? (
              <div className="p-8 text-center text-slate-500">Loading issues...</div>
            ) : bridgeIssues.length === 0 ? (
              <div className="p-8 text-center text-slate-400">No distress issues logged for this asset. Condition is within normal bounds.</div>
            ) : (
              <div className="divide-y divide-slate-200">
                {bridgeIssues.map((iss: any) => (
                  <div key={iss.id} className="p-4 hover:bg-slate-50 transition-colors space-y-3">
                    <div className="flex justify-between items-start">
                      <div className="space-y-1">
                        <div className="flex items-center gap-2">
                          <span className={`text-xs px-2 py-0.5 rounded-full font-bold uppercase ${
                            iss.severity === 'CRITICAL' ? 'bg-red-600 text-white' :
                            iss.severity === 'HIGH' ? 'bg-amber-500 text-white' : 'bg-slate-100 text-slate-700'
                          }`}>
                            {iss.severity} Priority
                          </span>
                          <span className="font-bold text-sm text-slate-900">{iss.issue_type.replace(/_/g, ' ')}</span>
                          <span className="text-xs text-slate-500">Source: {iss.source.replace(/_/g, ' ')}</span>
                        </div>
                        <p className="text-xs text-slate-700 font-medium">{iss.description}</p>
                        {iss.location_details && (
                          <div className="text-[11px] text-slate-500">Location: {iss.location_details}</div>
                        )}
                      </div>

                      <span className={`text-xs px-2 py-0.5 rounded font-semibold ${
                        iss.status === 'RESOLVED' ? 'bg-emerald-100 text-emerald-800' : 'bg-amber-100 text-amber-800'
                      }`}>
                        {iss.status}
                      </span>
                    </div>

                    <div className="flex items-center justify-between text-xs pt-1 border-t border-slate-100 text-slate-500">
                      <div>
                        Assigned Inspector: <span className="font-semibold text-slate-700">{iss.assigned_inspector_name || 'Unassigned'}</span>
                        {iss.assigned_engineer_name && ` &bull; Supervisor: ${iss.assigned_engineer_name}`}
                      </div>
                      <Link
                        to="/issues"
                        className="text-xs text-blue-600 font-semibold hover:underline"
                      >
                        Manage in Distress Registry &rarr;
                      </Link>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        )}

        {/* Tab 5: Inspections & Audit */}
        {activeTab === 'inspections' && (
          <div className="bg-white rounded-lg shadow-sm border border-slate-200 overflow-hidden">
            <div className="p-4 border-b border-slate-200 bg-slate-50 flex justify-between items-center">
              <div>
                <h3 className="text-base font-semibold text-slate-900">Inspection & Field Survey History</h3>
                <p className="text-xs text-slate-500">MoRTH audit standard: Anti-fraud Geofence verification, photo evidence, and EE counter-signatures.</p>
              </div>
              {hasPermission('inspection:create') && (
                <Link
                  to={`/bridges/${bridge.bridge_id}/inspections/new`}
                  className="px-3.5 py-1.5 bg-blue-600 hover:bg-blue-700 text-white rounded-md text-xs font-semibold shadow-sm transition-colors flex items-center gap-1.5"
                >
                  <span>📍</span>
                  <span>Record On-Site Inspection</span>
                </Link>
              )}
            </div>

            {loadingInspections ? (
              <div className="p-8 text-center text-slate-500">Loading inspections...</div>
            ) : inspections.length === 0 ? (
              <div className="p-8 text-center text-slate-400">No inspections recorded for this bridge yet.</div>
            ) : (
              <div className="divide-y divide-slate-200">
                {inspections.map((insp: any) => (
                  <div key={insp.inspection_id} className="p-4 hover:bg-slate-50 transition-colors space-y-3">
                    <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-3">
                      <div>
                        <div className="flex items-center gap-2 flex-wrap">
                          <span className="text-sm font-bold text-slate-800">{insp.inspection_type} Inspection</span>
                          <ConditionBadge condition={insp.overall_condition} />

                          {/* Geofence Status Badge */}
                          {insp.geofence_verified ? (
                            <span className="text-[11px] px-2 py-0.5 bg-emerald-50 text-emerald-800 border border-emerald-200 rounded font-semibold flex items-center gap-1">
                              <span>📍</span> On-Site Presence Verified ({insp.geofence_distance_meters ?? 0}m)
                            </span>
                          ) : (
                            <span className="text-[11px] px-2 py-0.5 bg-amber-50 text-amber-800 border border-amber-200 rounded font-semibold flex items-center gap-1">
                              <span>⚠️</span> Remote Submission ({insp.geofence_distance_meters ? `${insp.geofence_distance_meters}m` : 'No GPS'})
                            </span>
                          )}

                          {insp.photo_evidence_url && (
                            <a
                              href={insp.photo_evidence_url}
                              target="_blank"
                              rel="noreferrer"
                              className="text-[11px] text-blue-600 hover:underline flex items-center gap-1 font-medium bg-blue-50 px-2 py-0.5 rounded border border-blue-100"
                            >
                              <span>📷</span> Photo Proof
                            </a>
                          )}
                        </div>

                        <div className="text-xs text-slate-500 mt-1">
                          Inspected on <span className="font-semibold text-slate-700">{insp.inspection_date}</span> by{' '}
                          <span className="font-medium text-slate-700">{insp.inspector_name}</span>
                          {insp.next_inspection_date && ` &bull; Next due: ${insp.next_inspection_date}`}
                        </div>

                        {insp.findings && (
                          <div className="text-xs text-slate-600 mt-2 bg-slate-50 p-2.5 rounded border border-slate-100">
                            <span className="font-semibold">Findings: </span>{insp.findings}
                          </div>
                        )}
                      </div>

                      <button
                        onClick={() =>
                          setExpandedInspection(
                            expandedInspection === insp.inspection_id ? null : insp.inspection_id
                          )
                        }
                        className="text-xs text-blue-600 font-semibold hover:underline px-2 py-1 whitespace-nowrap"
                      >
                        {expandedInspection === insp.inspection_id ? 'Hide Details' : 'View Components & Defects'}
                      </button>
                    </div>

                    {/* Executive Engineer Counter-Signature Box */}
                    {insp.counter_signed_by_name ? (
                      <div className="p-3 bg-emerald-50/70 border border-emerald-200 rounded-md text-xs text-emerald-900 flex items-start gap-2.5">
                        <span className="text-base">🛡️</span>
                        <div className="space-y-0.5">
                          <div className="font-bold flex items-center gap-2">
                            <span>Counter-Signed & Verified by {insp.counter_signed_by_name}</span>
                            <span className="text-[10px] text-emerald-700 font-mono font-normal">({insp.counter_signed_at})</span>
                          </div>
                          <div className="text-[11px] text-emerald-800">
                            <em>"{insp.verification_remarks}"</em>
                          </div>
                        </div>
                      </div>
                    ) : (
                      <div className="p-2.5 bg-slate-50 border border-slate-200 rounded-md text-xs flex justify-between items-center">
                        <span className="text-slate-500 flex items-center gap-1.5">
                          <span>⏳</span>
                          <span>Pending Executive Engineer Counter-Signature & Quality Sign-Off</span>
                        </span>

                        {isEngineer && (
                          <button
                            onClick={() => {
                              setCounterSignInsp(insp);
                              setCounterSignRemarks(
                                `Verified on-site survey and ratings for ${insp.inspection_type} inspection by ${user?.full_name}`
                              );
                            }}
                            className="px-3 py-1 bg-indigo-600 hover:bg-indigo-700 text-white rounded text-xs font-semibold shadow-xs transition-colors flex items-center gap-1"
                          >
                            <span>✍️</span>
                            <span>Counter-Sign Inspection</span>
                          </button>
                        )}
                      </div>
                    )}

                    {/* Expandable Component Ratings & Defects */}
                    {expandedInspection === insp.inspection_id && (
                      <div className="mt-4 pt-4 border-t border-slate-200 space-y-4">
                        {insp.components && insp.components.length > 0 && (
                          <div>
                            <div className="text-xs font-bold text-slate-700 uppercase mb-2">Component Ratings</div>
                            <div className="grid grid-cols-2 md:grid-cols-3 gap-2">
                              {insp.components.map((c: any) => (
                                <div key={c.component_id} className="p-2 bg-white rounded border border-slate-200 text-xs">
                                  <div className="font-medium text-slate-800">{c.component_type.replace(/_/g, ' ')}</div>
                                  <div className="flex justify-between items-center mt-1">
                                    <span className="text-slate-400">Rating:</span>
                                    <span className={`font-bold px-1.5 py-0.5 rounded text-[11px] ${
                                      c.condition_rating >= 4 ? 'bg-emerald-100 text-emerald-800' :
                                      c.condition_rating === 3 ? 'bg-amber-100 text-amber-800' : 'bg-red-100 text-red-800'
                                    }`}>
                                      {c.condition_rating} / 5
                                    </span>
                                  </div>
                                </div>
                              ))}
                            </div>
                          </div>
                        )}

                        {insp.defects && insp.defects.length > 0 && (
                          <div>
                            <div className="text-xs font-bold text-slate-700 uppercase mb-2">Identified Distresses & Defects</div>
                            <div className="space-y-1.5">
                              {insp.defects.map((d: any) => (
                                <div key={d.defect_id} className="p-2.5 bg-red-50/60 border border-red-200 rounded flex justify-between items-center text-xs">
                                  <div>
                                    <span className="font-semibold text-red-900">{d.defect_type}: </span>
                                    <span className="text-slate-700">{d.description}</span>
                                  </div>
                                  <span className="px-2 py-0.5 bg-red-600 text-white rounded text-[10px] font-bold">
                                    {d.severity}
                                  </span>
                                </div>
                              ))}
                            </div>
                          </div>
                        )}
                      </div>
                    )}
                  </div>
                ))}
              </div>
            )}
          </div>
        )}

        {/* Tab 6: Procurement & Maintenance Workflow */}
        {activeTab === 'maintenance' && (
          <div className="bg-white rounded-lg shadow-sm border border-slate-200 overflow-hidden">
            <div className="p-4 border-b border-slate-200 bg-slate-50 flex justify-between items-center">
              <div>
                <h3 className="text-base font-semibold text-slate-900">Government Procurement & Maintenance Pipeline</h3>
                <p className="text-xs text-slate-500">
                  MoRTH / PWD 6-Stage Standard: Reported &rarr; DPR Estimated &rarr; Sanctioned (AA) &rarr; Tender Awarded &rarr; In Progress &rarr; Verified
                </p>
              </div>
              {hasPermission('maintenance:create') && (
                <button
                  onClick={() => setShowMaintModal(true)}
                  className="px-3.5 py-1.5 bg-blue-600 hover:bg-blue-700 text-white rounded-md text-xs font-semibold shadow-sm transition-colors"
                >
                  + Report Issue / Request Work
                </button>
              )}
            </div>

            {loadingMaint ? (
              <div className="p-8 text-center text-slate-500">Loading maintenance records...</div>
            ) : maintenanceRecords.length === 0 ? (
              <div className="p-8 text-center text-slate-400">No maintenance actions currently logged for this bridge.</div>
            ) : (
              <div className="divide-y divide-slate-200">
                {maintenanceRecords.map((m: any) => (
                  <div key={m.maintenance_id} className="p-5 hover:bg-slate-50/50 transition-colors space-y-4">
                    {/* Header Row */}
                    <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-3">
                      <div className="flex items-center gap-2.5 flex-wrap">
                        <span className="font-bold text-sm text-slate-900">{m.maintenance_type.replace(/_/g, ' ')}</span>
                        <PriorityBadge priority={m.priority} />
                        <span className={`text-xs px-2.5 py-0.5 rounded-full font-bold ${
                          m.status === 'VERIFIED' ? 'bg-emerald-100 text-emerald-800' :
                          m.status === 'COMPLETED' ? 'bg-blue-100 text-blue-800' :
                          m.status === 'IN_PROGRESS' ? 'bg-amber-100 text-amber-800' :
                          m.status === 'TENDER_AWARDED' ? 'bg-purple-100 text-purple-800' :
                          m.status === 'SANCTIONED' ? 'bg-indigo-100 text-indigo-800' :
                          m.status === 'ESTIMATED' ? 'bg-cyan-100 text-cyan-800' : 'bg-slate-100 text-slate-700'
                        }`}>
                          {m.status.replace(/_/g, ' ')}
                        </span>
                      </div>

                      <div className="text-xs text-slate-400 font-mono">
                        Reported: {m.reported_date}
                      </div>
                    </div>

                    {/* Issue Description */}
                    <p className="text-xs text-slate-700 font-medium">{m.issue_description}</p>

                    {/* MoRTH 6-Stage Visual Stepper */}
                    <div className="grid grid-cols-2 sm:grid-cols-6 gap-2 text-center text-[10px] font-bold uppercase">
                      {[
                        { key: 'REPORTED', label: '1. Reported' },
                        { key: 'ESTIMATED', label: '2. DPR Estimated' },
                        { key: 'SANCTIONED', label: '3. Sanctioned (AA)' },
                        { key: 'TENDER_AWARDED', label: '4. Tender Issued' },
                        { key: 'IN_PROGRESS', label: '5. In Progress' },
                        { key: 'VERIFIED', label: '6. Verified & Closed' },
                      ].map((step, idx) => {
                        const stages = ['REPORTED', 'ESTIMATED', 'SANCTIONED', 'TENDER_AWARDED', 'IN_PROGRESS', 'COMPLETED', 'VERIFIED'];
                        const currentIdx = stages.indexOf(m.status);
                        const stepIdx = stages.indexOf(step.key);
                        const isPastOrCurrent = currentIdx >= stepIdx;

                        return (
                          <div
                            key={step.key}
                            className={`p-1.5 rounded border ${
                              isPastOrCurrent
                                ? 'bg-blue-600 text-white border-blue-600'
                                : 'bg-slate-100 text-slate-400 border-slate-200'
                            }`}
                          >
                            {step.label}
                          </div>
                        );
                      })}
                    </div>

                    {/* Procurement Detail Data Cards */}
                    <div className="grid grid-cols-1 sm:grid-cols-3 gap-2.5 text-xs pt-1">
                      {/* DPR Estimate Details */}
                      <div className="p-3 bg-slate-50 rounded-lg border border-slate-200 space-y-1">
                        <div className="text-[10px] text-slate-400 font-bold uppercase">Technical DPR Estimate</div>
                        <div className="text-sm font-bold text-slate-800">
                          ₹{m.estimated_cost ? m.estimated_cost.toLocaleString() : 'Pending'}
                        </div>
                        <div className="text-[11px] text-slate-500">
                          {m.estimated_by_name ? `Prepared by: ${m.estimated_by_name}` : 'Awaiting Executive Engineer DPR'}
                        </div>
                      </div>

                      {/* Financial Sanction (AA) */}
                      <div className="p-3 bg-slate-50 rounded-lg border border-slate-200 space-y-1">
                        <div className="text-[10px] text-slate-400 font-bold uppercase">Administrative Sanction (AA)</div>
                        <div className="text-sm font-bold text-slate-800">
                          {m.sanction_number ? `#${m.sanction_number}` : 'Unsanctioned'}
                        </div>
                        <div className="text-[11px] text-slate-500">
                          {m.sanctioned_amount ? `Sanctioned: ₹${m.sanctioned_amount.toLocaleString()}` : 'Awaiting Dept Head Sanction'}
                        </div>
                      </div>

                      {/* Tender & Contractor Allocation */}
                      <div className="p-3 bg-slate-50 rounded-lg border border-slate-200 space-y-1">
                        <div className="text-[10px] text-slate-400 font-bold uppercase">Contractor & Work Order</div>
                        <div className="text-sm font-bold text-slate-800 truncate">
                          {m.assigned_contractor || 'No Contractor Appointed'}
                        </div>
                        <div className="text-[11px] text-slate-500 truncate">
                          {m.work_order_number ? `WO: #${m.work_order_number}` : 'Tender not yet awarded'}
                        </div>
                      </div>
                    </div>

                    {/* Quality Verification / Completion Notes */}
                    {m.verified_by_name && (
                      <div className="p-3 bg-emerald-50 border border-emerald-200 rounded-lg text-xs text-emerald-900 flex items-center gap-2">
                        <span className="text-base">✅</span>
                        <div>
                          <span className="font-bold">Completion Verified & Audited by: {m.verified_by_name}</span>
                          <span className="text-emerald-700 ml-2">({m.verification_notes || 'All works certified as per MoRTH specifications'})</span>
                        </div>
                      </div>
                    )}

                    {/* Contextual Action Buttons per Role */}
                    <div className="flex flex-wrap items-center justify-between gap-3 pt-2 border-t border-slate-100">
                      <div className="text-[11px] text-slate-400 font-mono">
                        ID: {m.maintenance_id.slice(0, 8)}...
                      </div>

                      <div className="flex items-center gap-2">
                        {/* Step 1: REPORTED -> Executive Engineer Prepares DPR */}
                        {m.status === 'REPORTED' && (
                          <>
                            {isEngineer ? (
                              <button
                                onClick={() => {
                                  setProcurementModal({ maint: m, action: 'estimate' });
                                  setProcEstimateCost(m.estimated_cost?.toString() || '350000');
                                  setProcRemarks('DPR estimate prepared as per State PWD Schedule of Rates (SoR 2026).');
                                }}
                                className="px-3 py-1.5 bg-blue-600 hover:bg-blue-700 text-white rounded text-xs font-semibold shadow-xs transition-colors flex items-center gap-1.5"
                              >
                                <span>📐</span>
                                <span>Prepare DPR Estimate (EE)</span>
                              </button>
                            ) : (
                              <span className="text-xs text-slate-400 italic">Awaiting Executive Engineer DPR preparation</span>
                            )}
                          </>
                        )}

                        {/* Step 2: ESTIMATED -> Dept Head Grants AA Sanction */}
                        {m.status === 'ESTIMATED' && (
                          <>
                            {isDeptHead ? (
                              <button
                                onClick={() => {
                                  setProcurementModal({ maint: m, action: 'sanction' });
                                  setProcSanctionNo(`AA/PWD/2026/${Math.floor(100 + Math.random() * 900)}`);
                                  setProcSanctionedAmt(m.estimated_cost?.toString() || '350000');
                                  setProcRemarks('Administrative Approval and Financial Sanction accorded under Infrastructure Budget Head.');
                                }}
                                className="px-3 py-1.5 bg-indigo-600 hover:bg-indigo-700 text-white rounded text-xs font-semibold shadow-xs transition-colors flex items-center gap-1.5"
                              >
                                <span>🏛️</span>
                                <span>Grant Financial Sanction (AA)</span>
                              </button>
                            ) : (
                              <span className="text-xs text-slate-400 italic">Awaiting Department Head Administrative Approval</span>
                            )}
                          </>
                        )}

                        {/* Step 3: SANCTIONED -> Award Tender & Issue Work Order */}
                        {m.status === 'SANCTIONED' && (
                          <>
                            {isMaintenanceOfficer ? (
                              <button
                                onClick={() => {
                                  setProcurementModal({ maint: m, action: 'award_tender' });
                                  setProcTenderNo(`NIT/NHAI/2026/${Math.floor(10 + Math.random() * 90)}`);
                                  setProcWorkOrderNo(`WO-PWD-${Math.floor(1000 + Math.random() * 9000)}`);
                                  setProcTenderVal(m.sanctioned_amount?.toString() || '345000');
                                  setProcContractor('Larsen & Toubro Infrastructure Ltd.');
                                  setProcRemarks('E-tender bids evaluated; contract awarded to lowest conforming bidder L1.');
                                }}
                                className="px-3 py-1.5 bg-purple-600 hover:bg-purple-700 text-white rounded text-xs font-semibold shadow-xs transition-colors flex items-center gap-1.5"
                              >
                                <span>📜</span>
                                <span>Issue Tender & Award Work Order</span>
                              </button>
                            ) : (
                              <span className="text-xs text-slate-400 italic">Awaiting Tendering & Procurement process</span>
                            )}
                          </>
                        )}

                        {/* Step 4: TENDER_AWARDED -> Start Work */}
                        {m.status === 'TENDER_AWARDED' && isMaintenanceOfficer && (
                          <button
                            onClick={() =>
                              updateMaintStatusMutation.mutate({
                                maintId: m.maintenance_id,
                                action: 'start',
                                remarks: 'Contractor mobilized equipment on site; physical execution initiated.',
                              })
                            }
                            className="px-3 py-1.5 bg-amber-600 hover:bg-amber-700 text-white rounded text-xs font-semibold shadow-xs transition-colors flex items-center gap-1.5"
                          >
                            <span>🚜</span>
                            <span>Mobilize & Start Work</span>
                          </button>
                        )}

                        {/* Step 5: IN_PROGRESS -> Mark Work Completed */}
                        {m.status === 'IN_PROGRESS' && isMaintenanceOfficer && (
                          <button
                            onClick={() => {
                              setProcurementModal({ maint: m, action: 'complete' });
                              setProcActualCost(m.tender_value?.toString() || m.estimated_cost?.toString() || '340000');
                              setProcRemarks('Physical structural repairs successfully completed as per engineering drawings.');
                            }}
                            className="px-3 py-1.5 bg-blue-600 hover:bg-blue-700 text-white rounded text-xs font-semibold shadow-xs transition-colors flex items-center gap-1.5"
                          >
                            <span>🏁</span>
                            <span>Mark Physical Work Completed</span>
                          </button>
                        )}

                        {/* Step 6: COMPLETED -> Executive Engineer Quality Audit & Verification */}
                        {m.status === 'COMPLETED' && isEngineer && (
                          <button
                            onClick={() => {
                              setProcurementModal({ maint: m, action: 'verify' });
                              setProcRemarks(`Certified quality audit and load verification completed by ${user?.full_name}. Structure restored to operational traffic.`);
                            }}
                            className="px-3 py-1.5 bg-emerald-600 hover:bg-emerald-700 text-white rounded text-xs font-semibold shadow-xs transition-colors flex items-center gap-1.5"
                          >
                            <span>✅</span>
                            <span>Quality Audit: Verify & Close</span>
                          </button>
                        )}
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        )}

        {/* Tab 7: Lifecycle Timeline */}
        {activeTab === 'lifecycle' && (
          <div className="bg-white p-6 rounded-lg shadow-sm border border-slate-200">
            <div className="flex justify-between items-center border-b border-slate-100 pb-3 mb-6">
              <div>
                <h3 className="text-base font-semibold text-slate-900">Bridge Asset Lifecycle History</h3>
                <p className="text-xs text-slate-500">Immutable chronological history of all lifecycle transitions and milestones.</p>
              </div>
              {hasPermission('lifecycle:create') && (
                <button
                  onClick={() => setShowLifecycleModal(true)}
                  className="px-3.5 py-1.5 bg-blue-600 hover:bg-blue-700 text-white rounded-md text-xs font-semibold shadow-sm transition-colors"
                >
                  + Record Lifecycle Action
                </button>
              )}
            </div>

            {loadingLifecycle ? (
              <div className="p-8 text-center text-slate-500">Loading timeline...</div>
            ) : lifecycleEvents.length === 0 ? (
              <div className="p-8 text-center text-slate-400">No lifecycle events recorded.</div>
            ) : (
              <div className="relative pl-6 space-y-6 before:absolute before:left-2.5 before:top-2 before:bottom-2 before:w-0.5 before:bg-slate-200">
                {lifecycleEvents.map((evt: any) => (
                  <div key={evt.event_id} className="relative">
                    <div className="absolute -left-6 top-1 w-3.5 h-3.5 rounded-full bg-blue-600 border-2 border-white shadow-sm ring-2 ring-blue-100" />
                    <div>
                      <div className="flex items-center gap-2 flex-wrap">
                        <span className="text-sm font-bold text-slate-900">{evt.event_type.replace(/_/g, ' ')}</span>
                        {evt.previous_status && evt.new_status && evt.previous_status !== evt.new_status && (
                          <span className="text-[11px] font-semibold text-slate-600 bg-slate-100 px-2 py-0.5 rounded border border-slate-200">
                            {evt.previous_status} &rarr; {evt.new_status}
                          </span>
                        )}
                        <span className="text-xs text-slate-400 font-mono ml-auto">
                          {evt.event_date}
                        </span>
                      </div>
                      <p className="text-xs text-slate-600 mt-1">{evt.description}</p>
                      <div className="text-[11px] text-slate-400 mt-1">
                        Recorded by: <span className="text-slate-600 font-medium">{evt.performed_by_name}</span> &bull; {evt.department}
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        )}
      </div>

      {/* Modal: Procurement Workflow Actions */}
      {procurementModal && (
        <div className="fixed inset-0 bg-black/50 z-50 flex items-center justify-center p-4">
          <div className="bg-white rounded-xl max-w-lg w-full p-6 space-y-4 shadow-2xl">
            <div className="flex justify-between items-center border-b border-slate-100 pb-3">
              <h3 className="text-lg font-bold text-slate-900 flex items-center gap-2">
                {procurementModal.action === 'estimate' && '📐 Prepare Technical DPR / SoR Estimate'}
                {procurementModal.action === 'sanction' && '🏛️ Grant Administrative Approval (AA) & Sanction'}
                {procurementModal.action === 'award_tender' && '📜 Issue Tender & Award Work Order'}
                {procurementModal.action === 'complete' && '🏁 Record Physical Completion & Expenditure'}
                {procurementModal.action === 'verify' && '✅ Executive Engineer Quality Audit & Verification'}
              </h3>
              <button onClick={() => setProcurementModal(null)} className="text-slate-400 hover:text-slate-600 text-lg">
                &times;
              </button>
            </div>

            <form onSubmit={handleProcurementSubmit} className="space-y-4">
              {/* DPR Estimate Fields */}
              {procurementModal.action === 'estimate' && (
                <div>
                  <label className="block text-xs font-semibold text-slate-700 mb-1">
                    Detailed Project Report (DPR) Cost Estimate (INR) *
                  </label>
                  <input
                    type="number"
                    value={procEstimateCost}
                    onChange={e => setProcEstimateCost(e.target.value)}
                    className="w-full px-3 py-2 border border-slate-300 rounded text-sm font-semibold"
                    required
                  />
                  <p className="text-[11px] text-slate-500 mt-1">
                    Calculated by Executive Engineer using Schedule of Rates (SoR) and distress quantities.
                  </p>
                </div>
              )}

              {/* Administrative Sanction Fields */}
              {procurementModal.action === 'sanction' && (
                <>
                  <div>
                    <label className="block text-xs font-semibold text-slate-700 mb-1">
                      Administrative Approval (AA) Order Number *
                    </label>
                    <input
                      type="text"
                      value={procSanctionNo}
                      onChange={e => setProcSanctionNo(e.target.value)}
                      className="w-full px-3 py-2 border border-slate-300 rounded text-sm font-mono"
                      required
                    />
                  </div>
                  <div>
                    <label className="block text-xs font-semibold text-slate-700 mb-1">
                      Sanctioned Budget Allocation (INR) *
                    </label>
                    <input
                      type="number"
                      value={procSanctionedAmt}
                      onChange={e => setProcSanctionedAmt(e.target.value)}
                      className="w-full px-3 py-2 border border-slate-300 rounded text-sm font-semibold"
                      required
                    />
                  </div>
                </>
              )}

              {/* Tender & Work Order Fields */}
              {procurementModal.action === 'award_tender' && (
                <>
                  <div className="grid grid-cols-2 gap-3">
                    <div>
                      <label className="block text-xs font-semibold text-slate-700 mb-1">
                        Notice Inviting Tender (NIT) *
                      </label>
                      <input
                        type="text"
                        value={procTenderNo}
                        onChange={e => setProcTenderNo(e.target.value)}
                        className="w-full px-3 py-2 border border-slate-300 rounded text-sm font-mono"
                        required
                      />
                    </div>
                    <div>
                      <label className="block text-xs font-semibold text-slate-700 mb-1">
                        Work Order Number *
                      </label>
                      <input
                        type="text"
                        value={procWorkOrderNo}
                        onChange={e => setProcWorkOrderNo(e.target.value)}
                        className="w-full px-3 py-2 border border-slate-300 rounded text-sm font-mono"
                        required
                      />
                    </div>
                  </div>
                  <div>
                    <label className="block text-xs font-semibold text-slate-700 mb-1">
                      Contract Award Value (INR) *
                    </label>
                    <input
                      type="number"
                      value={procTenderVal}
                      onChange={e => setProcTenderVal(e.target.value)}
                      className="w-full px-3 py-2 border border-slate-300 rounded text-sm font-semibold"
                      required
                    />
                  </div>
                  <div>
                    <label className="block text-xs font-semibold text-slate-700 mb-1">
                      Awarded Contractor / Agency Name *
                    </label>
                    <input
                      type="text"
                      value={procContractor}
                      onChange={e => setProcContractor(e.target.value)}
                      className="w-full px-3 py-2 border border-slate-300 rounded text-sm"
                      required
                    />
                  </div>
                </>
              )}

              {/* Physical Completion Fields */}
              {procurementModal.action === 'complete' && (
                <div>
                  <label className="block text-xs font-semibold text-slate-700 mb-1">
                    Actual Final Expenditure (INR) *
                  </label>
                  <input
                    type="number"
                    value={procActualCost}
                    onChange={e => setProcActualCost(e.target.value)}
                    className="w-full px-3 py-2 border border-slate-300 rounded text-sm font-semibold"
                    required
                  />
                </div>
              )}

              {/* Remarks Field (Common) */}
              <div>
                <label className="block text-xs font-semibold text-slate-700 mb-1">
                  Official Record Remarks / Audit Notes
                </label>
                <textarea
                  rows={2}
                  value={procRemarks}
                  onChange={e => setProcRemarks(e.target.value)}
                  className="w-full px-3 py-2 border border-slate-300 rounded text-sm"
                />
              </div>

              <div className="flex justify-end gap-2 pt-2 border-t border-slate-100">
                <button
                  type="button"
                  onClick={() => setProcurementModal(null)}
                  className="px-4 py-2 border border-slate-300 rounded-lg text-sm text-slate-700 hover:bg-slate-50 font-medium"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={updateMaintStatusMutation.isPending}
                  className="px-5 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg text-sm font-semibold shadow-xs"
                >
                  {updateMaintStatusMutation.isPending ? 'Processing...' : 'Confirm Action'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Modal: Counter-Sign Field Inspection */}
      {counterSignInsp && (
        <div className="fixed inset-0 bg-black/50 z-50 flex items-center justify-center p-4">
          <div className="bg-white rounded-xl max-w-md w-full p-6 space-y-4 shadow-2xl">
            <div className="flex justify-between items-center border-b border-slate-100 pb-3">
              <h3 className="text-lg font-bold text-slate-900 flex items-center gap-2">
                <span>🛡️</span> Counter-Sign Field Inspection Report
              </h3>
              <button onClick={() => setCounterSignInsp(null)} className="text-slate-400 hover:text-slate-600 text-lg">
                &times;
              </button>
            </div>

            <div className="p-3 bg-slate-50 border border-slate-200 rounded text-xs text-slate-700 space-y-1">
              <div><strong>Survey Type:</strong> {counterSignInsp.inspection_type} Inspection</div>
              <div><strong>Survey Date:</strong> {counterSignInsp.inspection_date}</div>
              <div><strong>Field Inspector:</strong> {counterSignInsp.inspector_name}</div>
              <div><strong>Geofence Status:</strong> {counterSignInsp.geofence_verified ? '📍 Verified On-Site' : '⚠️ Remote Submission Warning'}</div>
            </div>

            <form
              onSubmit={e => {
                e.preventDefault();
                counterSignMutation.mutate({
                  inspId: counterSignInsp.inspection_id,
                  remarks: counterSignRemarks,
                });
              }}
              className="space-y-4"
            >
              <div>
                <label className="block text-xs font-semibold text-slate-700 mb-1">
                  Executive Engineer Verification Remarks *
                </label>
                <textarea
                  rows={3}
                  value={counterSignRemarks}
                  onChange={e => setCounterSignRemarks(e.target.value)}
                  className="w-full px-3 py-2 border border-slate-300 rounded text-sm"
                  required
                />
              </div>

              <div className="flex justify-end gap-2 pt-2 border-t border-slate-100">
                <button
                  type="button"
                  onClick={() => setCounterSignInsp(null)}
                  className="px-4 py-2 border border-slate-300 rounded-lg text-sm text-slate-700 hover:bg-slate-50 font-medium"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={counterSignMutation.isPending}
                  className="px-5 py-2 bg-indigo-600 hover:bg-indigo-700 text-white rounded-lg text-sm font-semibold shadow-xs"
                >
                  {counterSignMutation.isPending ? 'Signing...' : 'Affix Official Counter-Signature'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Modal: Report Maintenance */}
      {showMaintModal && (
        <div className="fixed inset-0 bg-black/40 z-50 flex items-center justify-center p-4">
          <div className="bg-white rounded-lg max-w-md w-full p-6 space-y-4 shadow-xl">
            <h3 className="text-lg font-bold text-slate-900">Report Bridge Maintenance Issue</h3>
            <form onSubmit={handleCreateMaintenance} className="space-y-4">
              <div>
                <label className="block text-xs font-semibold text-slate-700 mb-1">Maintenance Type</label>
                <select
                  value={maintType}
                  onChange={e => setMaintType(e.target.value)}
                  className="w-full px-3 py-2 border border-slate-300 rounded text-sm"
                >
                  <option value="ROUTINE">Routine Maintenance</option>
                  <option value="PREVENTIVE">Preventive Maintenance</option>
                  <option value="REPAIR">Structural Repair</option>
                  <option value="REHABILITATION">Full Rehabilitation</option>
                  <option value="EMERGENCY_REPAIR">Emergency Repair</option>
                </select>
              </div>
              <div>
                <label className="block text-xs font-semibold text-slate-700 mb-1">Priority</label>
                <select
                  value={maintPriority}
                  onChange={e => setMaintPriority(e.target.value)}
                  className="w-full px-3 py-2 border border-slate-300 rounded text-sm"
                >
                  <option value="LOW">Low</option>
                  <option value="MEDIUM">Medium</option>
                  <option value="HIGH">High</option>
                  <option value="CRITICAL">Critical</option>
                </select>
              </div>
              <div>
                <label className="block text-xs font-semibold text-slate-700 mb-1">Initial Rough Cost Estimate (INR)</label>
                <input
                  type="number"
                  value={maintCost}
                  onChange={e => setMaintCost(e.target.value)}
                  className="w-full px-3 py-2 border border-slate-300 rounded text-sm"
                  required
                />
              </div>
              <div>
                <label className="block text-xs font-semibold text-slate-700 mb-1">Issue Description</label>
                <textarea
                  rows={3}
                  value={maintDesc}
                  onChange={e => setMaintDesc(e.target.value)}
                  placeholder="Detail the issue, observed distress, and immediate requirements..."
                  className="w-full px-3 py-2 border border-slate-300 rounded text-sm"
                  required
                />
              </div>
              <div className="flex justify-end gap-2 pt-2">
                <button
                  type="button"
                  onClick={() => setShowMaintModal(false)}
                  className="px-3 py-1.5 border border-slate-300 rounded text-sm text-slate-700 hover:bg-slate-50"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={createMaintMutation.isPending}
                  className="px-4 py-1.5 bg-blue-600 text-white rounded text-sm font-semibold hover:bg-blue-700 disabled:opacity-50"
                >
                  Submit Report
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Modal: Record Lifecycle Action */}
      {showLifecycleModal && (
        <div className="fixed inset-0 bg-black/40 z-50 flex items-center justify-center p-4">
          <div className="bg-white rounded-lg max-w-md w-full p-6 space-y-4 shadow-xl">
            <h3 className="text-lg font-bold text-slate-900">Log Lifecycle Status Action</h3>
            <p className="text-xs text-slate-500">
              Trigger a validated status transition governed by the lifecycle state machine.
            </p>
            <form onSubmit={handleCreateLifecycle} className="space-y-4">
              <div>
                <label className="block text-xs font-semibold text-slate-700 mb-1">Lifecycle Action / Event</label>
                <select
                  value={lifecycleType}
                  onChange={e => setLifecycleType(e.target.value)}
                  className="w-full px-3 py-2 border border-slate-300 rounded text-sm"
                >
                  <option value="MAINTENANCE_STARTED">MAINTENANCE_STARTED &rarr; UNDER_MAINTENANCE</option>
                  <option value="MAINTENANCE_COMPLETED">MAINTENANCE_COMPLETED &rarr; OPERATIONAL</option>
                  <option value="REHABILITATION_STARTED">REHABILITATION_STARTED &rarr; UNDER_REHABILITATION</option>
                  <option value="REHABILITATION_COMPLETED">REHABILITATION_COMPLETED &rarr; OPERATIONAL</option>
                  <option value="CLOSED">CLOSED &rarr; Traffic Suspended</option>
                  <option value="REOPENED">REOPENED &rarr; Restored to Traffic</option>
                  <option value="DECOMMISSIONED">DECOMMISSIONED &rarr; Permanent Retirement</option>
                </select>
              </div>
              <div>
                <label className="block text-xs font-semibold text-slate-700 mb-1">Official Remarks & Details</label>
                <textarea
                  rows={3}
                  value={lifecycleDesc}
                  onChange={e => setLifecycleDesc(e.target.value)}
                  placeholder="Document reason for transition, authority order number, or department approval..."
                  className="w-full px-3 py-2 border border-slate-300 rounded text-sm"
                  required
                />
              </div>
              <div className="flex justify-end gap-2 pt-2">
                <button
                  type="button"
                  onClick={() => setShowLifecycleModal(false)}
                  className="px-3 py-1.5 border border-slate-300 rounded text-sm text-slate-700 hover:bg-slate-50"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={createLifecycleMutation.isPending}
                  className="px-4 py-1.5 bg-blue-600 text-white rounded text-sm font-semibold hover:bg-blue-700 disabled:opacity-50"
                >
                  Record Transition
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Modal: Delete Bridge Confirmation */}
      {showDeleteModal && (
        <div className="fixed inset-0 bg-black/50 z-50 flex items-center justify-center p-4">
          <div className="bg-white rounded-lg max-w-md w-full p-6 space-y-4 shadow-xl">
            <div className="flex items-center gap-3 text-red-600">
              <div className="w-10 h-10 rounded-full bg-red-100 flex items-center justify-center flex-shrink-0">
                <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
                </svg>
              </div>
              <div>
                <h3 className="text-base font-bold text-slate-900">Delete Bridge Asset</h3>
                <p className="text-xs text-slate-500">Restricted Administrator Operation</p>
              </div>
            </div>

            <p className="text-xs text-slate-600 leading-relaxed">
              Are you sure you want to permanently delete <strong className="text-slate-900">{bridge.bridge_name}</strong> (<span className="font-mono">{bridge.bridge_code}</span>)?
            </p>
            <div className="p-3 bg-red-50 border border-red-200 rounded text-xs text-red-700 space-y-1">
              <div className="font-bold">Warning: Cascade Deletion</div>
              <div>All associated location coordinates, engineering specifications, historical inspection surveys, and maintenance logs will be permanently deleted.</div>
              <div className="font-semibold text-[11px] pt-1">This event will be logged in the immutable audit log.</div>
            </div>

            <div className="flex justify-end gap-2 pt-2 border-t border-slate-100">
              <button
                type="button"
                onClick={() => setShowDeleteModal(false)}
                className="px-3 py-1.5 border border-slate-300 rounded text-xs font-semibold text-slate-700 hover:bg-slate-50"
              >
                Cancel
              </button>
              <button
                type="button"
                onClick={() => deleteMutation.mutate()}
                disabled={deleteMutation.isPending}
                className="px-4 py-1.5 bg-red-600 text-white rounded text-xs font-bold hover:bg-red-700 disabled:opacity-50"
              >
                {deleteMutation.isPending ? 'Deleting...' : 'Confirm Permanent Deletion'}
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Modal: Report Distress on this Bridge */}
      {showReportIssueModal && (
        <div className="fixed inset-0 bg-black/50 z-50 flex items-center justify-center p-4">
          <div className="bg-white rounded-xl max-w-lg w-full p-6 space-y-4 shadow-2xl">
            <div className="flex justify-between items-center border-b border-slate-100 pb-3">
              <h3 className="text-lg font-bold text-slate-900 flex items-center gap-2">
                <span>⚠️</span> Report Structural Distress on {bridge.bridge_name}
              </h3>
              <button onClick={() => setShowReportIssueModal(false)} className="text-slate-400 hover:text-slate-600 text-lg">
                &times;
              </button>
            </div>

            {createBridgeIssueMutation.isError && (
              <div className="p-3 bg-red-50 border border-red-200 text-red-700 text-xs rounded-lg">
                <strong>Submission Error:</strong> {(createBridgeIssueMutation.error as any)?.response?.data?.detail || createBridgeIssueMutation.error?.message}
              </div>
            )}

            <form
              onSubmit={e => {
                e.preventDefault();
                createBridgeIssueMutation.mutate({
                  bridge_id: id!,
                  source: issueSource,
                  issue_type: issueType,
                  severity: issueSeverity,
                  description: issueDesc,
                  location_details: issueLocation,
                  photo_url: issuePhoto,
                });
              }}
              className="space-y-4"
            >
              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block text-xs font-semibold text-slate-700 mb-1">Discovery Source</label>
                  <select
                    value={issueSource}
                    onChange={e => setIssueSource(e.target.value)}
                    className="w-full px-3 py-2 border border-slate-300 rounded text-sm"
                  >
                    <option value="CITIZEN_REPORT">Citizen / Public Distress</option>
                    <option value="FIELD_INSPECTION">Field Inspection Escalation</option>
                    <option value="SENSOR_BHI_ALERT">Automated BHI / Sensor Alert</option>
                  </select>
                </div>
                <div>
                  <label className="block text-xs font-semibold text-slate-700 mb-1">Severity Level</label>
                  <select
                    value={issueSeverity}
                    onChange={e => setIssueSeverity(e.target.value)}
                    className="w-full px-3 py-2 border border-slate-300 rounded text-sm font-semibold"
                  >
                    <option value="LOW">Low</option>
                    <option value="MEDIUM">Medium</option>
                    <option value="HIGH">High</option>
                    <option value="CRITICAL">Critical</option>
                  </select>
                </div>
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-700 mb-1">Distress Classification</label>
                <select
                  value={issueType}
                  onChange={e => setIssueType(e.target.value)}
                  className="w-full px-3 py-2 border border-slate-300 rounded text-sm"
                >
                  <option value="STRUCTURAL_CRACK">Severe Structural Crack / Spalling</option>
                  <option value="BEARING_FAILURE">Bearing Displacement / Distortion</option>
                  <option value="SCOUR_EROSION">Pier / Abutment Scour Erosion</option>
                  <option value="POTHOLES_SURFACING">Deck Potholes & Wear Course Rutting</option>
                  <option value="EXPANSION_JOINT_DAMAGE">Expansion Joint Rupture</option>
                  <option value="WATERLOGGING">Severe Waterlogging / Drainage Clog</option>
                  <option value="RAILING_DAMAGE">Crash Barrier / Parapet Impact</option>
                  <option value="OTHER">Other Distress</option>
                </select>
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-700 mb-1">Location on Structure</label>
                <input
                  type="text"
                  value={issueLocation}
                  onChange={e => setIssueLocation(e.target.value)}
                  placeholder="e.g. Pier 2 downstream pedestal, Span 3 left lane"
                  className="w-full px-3 py-2 border border-slate-300 rounded text-sm"
                />
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-700 mb-1">Detailed Description *</label>
                <textarea
                  rows={3}
                  value={issueDesc}
                  onChange={e => setIssueDesc(e.target.value)}
                  placeholder="Describe observed damage, crack width, safety risk..."
                  className="w-full px-3 py-2 border border-slate-300 rounded text-sm"
                  required
                />
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-700 mb-1">Photo Evidence URL</label>
                <input
                  type="url"
                  value={issuePhoto}
                  onChange={e => setIssuePhoto(e.target.value)}
                  className="w-full px-3 py-2 border border-slate-300 rounded text-sm"
                />
              </div>

              <div className="flex justify-end gap-2 pt-2 border-t border-slate-100">
                <button
                  type="button"
                  onClick={() => setShowReportIssueModal(false)}
                  className="px-4 py-2 border border-slate-300 rounded-lg text-sm text-slate-700 hover:bg-slate-50"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={createBridgeIssueMutation.isPending}
                  className="px-5 py-2 bg-red-600 hover:bg-red-700 text-white rounded-lg text-sm font-semibold shadow-xs"
                >
                  {createBridgeIssueMutation.isPending ? 'Submitting...' : 'Submit Distress Report'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}