import React, { useState, useEffect } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { Link, useNavigate } from 'react-router-dom';
import { api } from '../api/endpoints';
import { useAuth } from '../context/AuthContext';
import { useAsset } from '../context/AssetContext';
import { DistressIssue, AssignableOfficer } from '../types';

export default function IssueRegistry() {
  const { user } = useAuth();
  const { activeAssetType } = useAsset();
  const queryClient = useQueryClient();
  const navigate = useNavigate();

  const [activeFilter, setActiveFilter] = useState<'ALL' | 'CRITICAL' | 'MY_ASSIGNED' | 'OPEN' | 'RESOLVED'>('ALL');
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [selectedIssueForAssign, setSelectedIssueForAssign] = useState<DistressIssue | null>(null);
  const [selectedIssueForResolve, setSelectedIssueForResolve] = useState<DistressIssue | null>(null);

  // New Issue Form State
  const [selectedBridgeId, setSelectedBridgeId] = useState('');
  const [issueSource, setIssueSource] = useState('FIELD_INSPECTION');
  const [issueType, setIssueType] = useState('STRUCTURAL_CRACK');
  const [severity, setSeverity] = useState('HIGH');
  const [description, setDescription] = useState('');
  const [locationDetails, setLocationDetails] = useState('');
  const [photoUrl, setPhotoUrl] = useState('https://images.unsplash.com/photo-1545558014-8692077e9b5c?auto=format&fit=crop&w=800&q=80');

  // Assignment Modal State
  const [assignInspectorId, setAssignInspectorId] = useState('');
  const [assignEngineerId, setAssignEngineerId] = useState('');
  const [targetDate, setTargetDate] = useState(() => {
    const d = new Date();
    d.setDate(d.getDate() + 7);
    return d.toISOString().split('T')[0];
  });
  const [assignRemarks, setAssignRemarks] = useState('');

  // Resolve Modal State
  const [resolveStatus, setResolveStatus] = useState('RESOLVED');
  const [resolveRemarks, setResolveRemarks] = useState('');

  // Queries
  const { data: issues = [], isLoading: loadingIssues } = useQuery({
    queryKey: ['issues', activeAssetType],
    queryFn: () => api.getIssues({ asset_type: activeAssetType === 'ALL' ? undefined : activeAssetType }),
  });

  const { data: bridgesData } = useQuery({
    queryKey: ['bridges-lookup'],
    queryFn: () => api.getBridges({ limit: 100 }),
  });

  const { data: assignableOfficers } = useQuery({
    queryKey: ['assignable-officers'],
    queryFn: () => api.getAssignableOfficers(),
  });

  // Mutations
  const createIssueMutation = useMutation({
    mutationFn: (data: any) => api.createIssue(data),
    onSuccess: () => {
      setShowCreateModal(false);
      setDescription('');
      setLocationDetails('');
      queryClient.invalidateQueries({ queryKey: ['issues'] });
    },
  });

  const assignIssueMutation = useMutation({
    mutationFn: ({ id, data }: { id: string; data: any }) => api.assignIssue(id, data),
    onSuccess: () => {
      setSelectedIssueForAssign(null);
      queryClient.invalidateQueries({ queryKey: ['issues'] });
    },
  });

  const resolveIssueMutation = useMutation({
    mutationFn: ({ id, data }: { id: string; data: any }) => api.resolveIssue(id, data),
    onSuccess: () => {
      setSelectedIssueForResolve(null);
      queryClient.invalidateQueries({ queryKey: ['issues'] });
    },
  });

  const handleCreateSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    const targetBridgeId = selectedBridgeId || bridgesList[0]?.bridge_id;
    if (!targetBridgeId) {
      alert("Please select an infrastructure asset.");
      return;
    }
    createIssueMutation.mutate({
      bridge_id: targetBridgeId,
      source: issueSource,
      issue_type: issueType,
      severity,
      description,
      location_details: locationDetails,
      photo_url: photoUrl,
    });
  };

  const handleAssignSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!selectedIssueForAssign) return;
    assignIssueMutation.mutate({
      id: selectedIssueForAssign.id,
      data: {
        assigned_inspector_id: assignInspectorId || undefined,
        assigned_engineer_id: assignEngineerId || undefined,
        target_completion_date: targetDate,
        remarks: assignRemarks,
      },
    });
  };

  const handleResolveSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!selectedIssueForResolve) return;
    resolveIssueMutation.mutate({
      id: selectedIssueForResolve.id,
      data: {
        status: resolveStatus,
        remarks: resolveRemarks,
      },
    });
  };

  const bridgesList = bridgesData?.items || [];
  const inspectors = assignableOfficers?.inspectors || [];
  const engineers = assignableOfficers?.engineers || [];

  useEffect(() => {
    if (bridgesList.length > 0 && !selectedBridgeId) {
      setSelectedBridgeId(bridgesList[0].bridge_id);
    }
  }, [bridgesList, selectedBridgeId]);

  // Filter issues
  const filteredIssues = issues.filter(issue => {
    if (activeFilter === 'CRITICAL') return issue.severity === 'CRITICAL' || issue.severity === 'HIGH';
    if (activeFilter === 'MY_ASSIGNED') {
      return (
        issue.assigned_inspector_id === user?.id ||
        issue.assigned_engineer_id === user?.id ||
        issue.reported_by === user?.id
      );
    }
    if (activeFilter === 'OPEN') return issue.status !== 'RESOLVED' && issue.status !== 'CLOSED';
    if (activeFilter === 'RESOLVED') return issue.status === 'RESOLVED' || issue.status === 'CLOSED';
    return true;
  });

  const isEngineerOrAdmin = ['EXECUTIVE_ENGINEER', 'DEPARTMENT_HEAD', 'ADMIN'].includes(user?.role || '');

  return (
    <div className="space-y-6 max-w-7xl mx-auto pb-12">
      {/* Top Header */}
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4 bg-white p-6 rounded-xl border border-slate-200 shadow-xs">
        <div>
          <div className="flex items-center gap-2">
            <span className="text-xl">🚨</span>
            <h1 className="text-2xl font-bold text-slate-900">Distress Incidents & Work Allocation</h1>
            <span className="text-xs px-2.5 py-0.5 rounded-full font-bold bg-amber-100 text-amber-800 border border-amber-200">
              {issues.length} Total Incidents
            </span>
          </div>
          <p className="text-sm text-slate-500 mt-1">
            Indian Government standard workflow for reporting structural defects, delegating inspection tasks, and assigning supervising engineers.
          </p>
        </div>

        <button
          onClick={() => {
            if (bridgesList.length > 0 && !selectedBridgeId) {
              setSelectedBridgeId(bridgesList[0].bridge_id);
            }
            setShowCreateModal(true);
          }}
          className="px-4 py-2 bg-red-600 hover:bg-red-700 text-white rounded-lg text-sm font-semibold shadow-xs flex items-center gap-2 transition-colors"
        >
          <span>⚠️</span>
          <span>Report Distress Incident</span>
        </button>
      </div>

      {/* Filter Tabs */}
      <div className="flex items-center gap-2 border-b border-slate-200 pb-2 overflow-x-auto">
        {[
          { key: 'ALL', label: 'All Incidents', count: issues.length },
          { key: 'CRITICAL', label: 'Critical / High Severity', count: issues.filter(i => i.severity === 'CRITICAL' || i.severity === 'HIGH').length },
          { key: 'OPEN', label: 'Active & Assigned', count: issues.filter(i => i.status !== 'RESOLVED' && i.status !== 'CLOSED').length },
          { key: 'MY_ASSIGNED', label: 'Assigned to Me', count: issues.filter(i => i.assigned_inspector_id === user?.id || i.assigned_engineer_id === user?.id).length },
          { key: 'RESOLVED', label: 'Resolved / Closed', count: issues.filter(i => i.status === 'RESOLVED' || i.status === 'CLOSED').length },
        ].map(tab => (
          <button
            key={tab.key}
            onClick={() => setActiveFilter(tab.key as any)}
            className={`px-3 py-1.5 rounded-md text-xs font-semibold whitespace-nowrap transition-colors flex items-center gap-1.5 ${
              activeFilter === tab.key
                ? 'bg-blue-600 text-white shadow-xs'
                : 'bg-white text-slate-600 border border-slate-200 hover:bg-slate-50'
            }`}
          >
            <span>{tab.label}</span>
            <span className={`text-[10px] px-1.5 py-0.2 rounded-full font-bold ${
              activeFilter === tab.key ? 'bg-blue-800 text-white' : 'bg-slate-100 text-slate-700'
            }`}>
              {tab.count}
            </span>
          </button>
        ))}
      </div>

      {/* Issues List */}
      {loadingIssues ? (
        <div className="p-12 text-center text-slate-500">Loading distress registry...</div>
      ) : filteredIssues.length === 0 ? (
        <div className="bg-white rounded-xl border border-slate-200 p-12 text-center space-y-3">
          <div className="text-4xl">🛡️</div>
          <div className="text-base font-bold text-slate-800">No distress issues matching this view</div>
          <p className="text-xs text-slate-500 max-w-md mx-auto">
            All structural assets are operating under normal conditions or matching filters are clear.
          </p>
        </div>
      ) : (
        <div className="grid grid-cols-1 gap-4">
          {filteredIssues.map(issue => (
            <div
              key={issue.id}
              className={`bg-white rounded-xl border p-5 transition-shadow hover:shadow-md space-y-4 ${
                issue.severity === 'CRITICAL'
                  ? 'border-red-300 ring-1 ring-red-100'
                  : issue.severity === 'HIGH'
                  ? 'border-amber-300'
                  : 'border-slate-200'
              }`}
            >
              <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-3 border-b border-slate-100 pb-3">
                <div className="flex items-center gap-2.5 flex-wrap">
                  <span className={`text-xs px-2.5 py-0.5 rounded-full font-bold uppercase ${
                    issue.severity === 'CRITICAL'
                      ? 'bg-red-600 text-white'
                      : issue.severity === 'HIGH'
                      ? 'bg-amber-500 text-white'
                      : issue.severity === 'MEDIUM'
                      ? 'bg-blue-100 text-blue-800'
                      : 'bg-slate-100 text-slate-700'
                  }`}>
                    {issue.severity} Priority
                  </span>

                  <span className="text-xs font-bold text-slate-900 bg-slate-100 px-2 py-0.5 rounded">
                    {issue.issue_type.replace(/_/g, ' ')}
                  </span>

                  <span className="text-xs text-slate-500">
                    Source: <span className="font-semibold text-slate-700">{issue.source.replace(/_/g, ' ')}</span>
                  </span>

                  <span className={`text-xs px-2 py-0.5 rounded font-semibold ${
                    issue.status === 'RESOLVED'
                      ? 'bg-emerald-100 text-emerald-800'
                      : issue.status === 'ASSIGNED'
                      ? 'bg-indigo-100 text-indigo-800'
                      : issue.status === 'UNDER_INSPECTION'
                      ? 'bg-purple-100 text-purple-800'
                      : 'bg-amber-100 text-amber-800'
                  }`}>
                    Status: {issue.status}
                  </span>
                </div>

                <div className="text-xs text-slate-400 font-mono">
                  Reported: {new Date(issue.created_at).toLocaleDateString()}
                </div>
              </div>

              {/* Main Content Info */}
              <div className="grid grid-cols-1 lg:grid-cols-12 gap-4">
                {/* Photo Preview if available */}
                {issue.photo_url && (
                  <div className="lg:col-span-3">
                    <img
                      src={issue.photo_url}
                      alt="Distress Proof"
                      className="w-full h-32 object-cover rounded-lg border border-slate-200"
                    />
                  </div>
                )}

                <div className={issue.photo_url ? 'lg:col-span-9 space-y-2' : 'lg:col-span-12 space-y-2'}>
                  <div className="flex items-center gap-2">
                    <Link
                      to={`/bridges/${issue.bridge_id}`}
                      className="text-base font-bold text-blue-600 hover:underline"
                    >
                      {issue.bridge_name || 'Infrastructure Asset'} ({issue.bridge_code})
                    </Link>
                    <span className="text-xs text-slate-500 font-medium">&bull; District: {issue.district || 'Gujarat'}</span>
                  </div>

                  <p className="text-xs text-slate-700 leading-relaxed font-medium">
                    {issue.description}
                  </p>

                  {issue.location_details && (
                    <div className="text-xs text-slate-500 flex items-center gap-1.5">
                      <span className="font-semibold text-slate-700">Specific Location:</span>
                      <span>{issue.location_details}</span>
                    </div>
                  )}

                  {/* Task Allocation Cards */}
                  <div className="grid grid-cols-1 sm:grid-cols-3 gap-2 pt-2 text-xs">
                    <div className="p-2 bg-slate-50 rounded border border-slate-100">
                      <div className="text-[10px] text-slate-400 uppercase font-bold">Assigned Inspector</div>
                      <div className="font-semibold text-slate-800 mt-0.5">
                        {issue.assigned_inspector_name ? `👷 ${issue.assigned_inspector_name}` : '⚠️ Unassigned'}
                      </div>
                    </div>

                    <div className="p-2 bg-slate-50 rounded border border-slate-100">
                      <div className="text-[10px] text-slate-400 uppercase font-bold">Supervising Engineer</div>
                      <div className="font-semibold text-slate-800 mt-0.5">
                        {issue.assigned_engineer_name ? `📐 ${issue.assigned_engineer_name}` : 'Not assigned'}
                      </div>
                    </div>

                    <div className="p-2 bg-slate-50 rounded border border-slate-100">
                      <div className="text-[10px] text-slate-400 uppercase font-bold">Target Date</div>
                      <div className="font-semibold text-slate-800 mt-0.5">
                        {issue.target_completion_date ? `📅 ${issue.target_completion_date}` : 'Not scheduled'}
                      </div>
                    </div>
                  </div>
                </div>
              </div>

              {/* Actions Footer */}
              <div className="flex flex-wrap items-center justify-between gap-3 pt-3 border-t border-slate-100">
                <div className="text-[11px] text-slate-500">
                  Reported by: <span className="font-semibold text-slate-700">{issue.reporter_name}</span> ({issue.reporter_role})
                </div>

                <div className="flex items-center gap-2">
                  {/* Executive Engineer / Dept Head can assign task */}
                  {isEngineerOrAdmin && issue.status !== 'RESOLVED' && (
                    <button
                      onClick={() => {
                        setSelectedIssueForAssign(issue);
                        setAssignInspectorId(issue.assigned_inspector_id || (inspectors[0]?.id || ''));
                        setAssignEngineerId(issue.assigned_engineer_id || (engineers[0]?.id || ''));
                        if (issue.target_completion_date) {
                          setTargetDate(issue.target_completion_date);
                        }
                      }}
                      className="px-3 py-1.5 bg-indigo-50 border border-indigo-200 text-indigo-700 hover:bg-indigo-100 rounded-lg text-xs font-semibold transition-colors flex items-center gap-1.5"
                    >
                      <span>📋</span>
                      <span>Assign / Reassign Task</span>
                    </button>
                  )}

                  {/* Inspector Action: Conduct Geofenced Inspection */}
                  {['INSPECTOR', 'EXECUTIVE_ENGINEER', 'ADMIN'].includes(user?.role || '') && issue.status !== 'RESOLVED' && (
                    <Link
                      to={`/bridges/${issue.bridge_id}/inspections/new`}
                      className="px-3 py-1.5 bg-blue-600 hover:bg-blue-700 text-white rounded-lg text-xs font-semibold shadow-xs transition-colors flex items-center gap-1.5"
                    >
                      <span>🔍</span>
                      <span>Conduct Field Inspection</span>
                    </Link>
                  )}

                  {/* Resolve Issue Button */}
                  {isEngineerOrAdmin && issue.status !== 'RESOLVED' && (
                    <button
                      onClick={() => {
                        setSelectedIssueForResolve(issue);
                        setResolveStatus('RESOLVED');
                      }}
                      className="px-3 py-1.5 bg-emerald-50 border border-emerald-200 text-emerald-800 hover:bg-emerald-100 rounded-lg text-xs font-semibold transition-colors"
                    >
                      Mark Resolved
                    </button>
                  )}
                </div>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Modal: Report Distress Incident */}
      {showCreateModal && (
        <div className="fixed inset-0 bg-black/50 z-50 flex items-center justify-center p-4">
          <div className="bg-white rounded-xl max-w-lg w-full p-6 space-y-4 shadow-2xl">
            <div className="flex justify-between items-center border-b border-slate-100 pb-3">
              <h3 className="text-lg font-bold text-slate-900 flex items-center gap-2">
                <span>⚠️</span> Report Structural Distress Incident
              </h3>
              <button onClick={() => setShowCreateModal(false)} className="text-slate-400 hover:text-slate-600 text-lg">
                &times;
              </button>
            </div>

            <form onSubmit={handleCreateSubmit} className="space-y-4">
              {createIssueMutation.isError && (
                <div className="p-3 bg-red-50 border border-red-200 text-red-700 text-xs rounded-lg">
                  <strong>Submission Error:</strong> {(createIssueMutation.error as any)?.response?.data?.detail || createIssueMutation.error?.message}
                </div>
              )}

              <div>
                <label className="block text-xs font-semibold text-slate-700 mb-1">Select Asset *</label>
                <select
                  value={selectedBridgeId || (bridgesList.length > 0 ? bridgesList[0].bridge_id : '')}
                  onChange={e => setSelectedBridgeId(e.target.value)}
                  className="w-full px-3 py-2 border border-slate-300 rounded-md text-sm"
                  required
                >
                  {bridgesList.map(b => (
                    <option key={b.bridge_id} value={b.bridge_id}>
                      {b.bridge_name} ({b.bridge_code}) &bull; {b.district}
                    </option>
                  ))}
                </select>
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block text-xs font-semibold text-slate-700 mb-1">Discovery Source</label>
                  <select
                    value={issueSource}
                    onChange={e => setIssueSource(e.target.value)}
                    className="w-full px-3 py-2 border border-slate-300 rounded-md text-sm"
                  >
                    <option value="FIELD_INSPECTION">Field Inspection Escalation</option>
                    <option value="CITIZEN_REPORT">Citizen / Public Distress</option>
                    <option value="SENSOR_BHI_ALERT">Automated BHI / Sensor Alert</option>
                  </select>
                </div>

                <div>
                  <label className="block text-xs font-semibold text-slate-700 mb-1">Severity Level</label>
                  <select
                    value={severity}
                    onChange={e => setSeverity(e.target.value)}
                    className="w-full px-3 py-2 border border-slate-300 rounded-md text-sm font-semibold"
                  >
                    <option value="LOW">Low</option>
                    <option value="MEDIUM">Medium</option>
                    <option value="HIGH">High</option>
                    <option value="CRITICAL">Critical</option>
                  </select>
                </div>
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-700 mb-1">Issue / Defect Classification</label>
                <select
                  value={issueType}
                  onChange={e => setIssueType(e.target.value)}
                  className="w-full px-3 py-2 border border-slate-300 rounded-md text-sm"
                >
                  <option value="STRUCTURAL_CRACK">Severe Structural Crack / Spalling</option>
                  <option value="BEARING_FAILURE">Bearing Displacement / Distortion</option>
                  <option value="SCOUR_EROSION">Pier / Abutment Scour Erosion</option>
                  <option value="POTHOLES_SURFACING">Deck Potholes & Wear Course Rutting</option>
                  <option value="EXPANSION_JOINT_DAMAGE">Expansion Joint Rupture</option>
                  <option value="WATERLOGGING">Severe Waterlogging / Clogged Drains</option>
                  <option value="RAILING_DAMAGE">Crash Barrier / Parapet Impact</option>
                  <option value="OTHER">Other Structural Distress</option>
                </select>
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-700 mb-1">Specific Location on Structure</label>
                <input
                  type="text"
                  value={locationDetails}
                  onChange={e => setLocationDetails(e.target.value)}
                  placeholder="e.g. Pier 3 downstream pier cap, Span 2 mid-deck"
                  className="w-full px-3 py-2 border border-slate-300 rounded-md text-sm"
                />
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-700 mb-1">Detailed Description *</label>
                <textarea
                  rows={3}
                  value={description}
                  onChange={e => setDescription(e.target.value)}
                  placeholder="Describe the nature of distress, observed width of cracks, traffic hazard..."
                  className="w-full px-3 py-2 border border-slate-300 rounded-md text-sm"
                  required
                />
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-700 mb-1">Geotagged Photo Proof URL</label>
                <input
                  type="url"
                  value={photoUrl}
                  onChange={e => setPhotoUrl(e.target.value)}
                  placeholder="https://..."
                  className="w-full px-3 py-2 border border-slate-300 rounded-md text-sm"
                />
              </div>

              <div className="flex justify-end gap-2 pt-2 border-t border-slate-100">
                <button
                  type="button"
                  onClick={() => setShowCreateModal(false)}
                  className="px-4 py-2 border border-slate-300 rounded-lg text-sm text-slate-700 hover:bg-slate-50 font-medium"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={createIssueMutation.isPending}
                  className="px-5 py-2 bg-red-600 hover:bg-red-700 text-white rounded-lg text-sm font-semibold shadow-xs"
                >
                  {createIssueMutation.isPending ? 'Logging Incident...' : 'Submit Distress Report'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Modal: Task Assignment */}
      {selectedIssueForAssign && (
        <div className="fixed inset-0 bg-black/50 z-50 flex items-center justify-center p-4">
          <div className="bg-white rounded-xl max-w-md w-full p-6 space-y-4 shadow-2xl">
            <div className="flex justify-between items-center border-b border-slate-100 pb-3">
              <h3 className="text-lg font-bold text-slate-900 flex items-center gap-2">
                <span>📋</span> Assign Officers & Schedule
              </h3>
              <button onClick={() => setSelectedIssueForAssign(null)} className="text-slate-400 hover:text-slate-600 text-lg">
                &times;
              </button>
            </div>

            <p className="text-xs text-slate-500">
              Formally delegate field verification to a designated Inspector and appoint an Executive Engineer supervisor for quality sign-off.
            </p>

            <form onSubmit={handleAssignSubmit} className="space-y-4">
              <div>
                <label className="block text-xs font-semibold text-slate-700 mb-1">Designated Field Inspector *</label>
                <select
                  value={assignInspectorId}
                  onChange={e => setAssignInspectorId(e.target.value)}
                  className="w-full px-3 py-2 border border-slate-300 rounded-md text-sm font-medium"
                  required
                >
                  <option value="">Select Field Inspector</option>
                  {inspectors.map(ins => (
                    <option key={ins.id} value={ins.id}>
                      {ins.full_name} ({ins.role}) &bull; {ins.department}
                    </option>
                  ))}
                </select>
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-700 mb-1">Supervising Executive Engineer</label>
                <select
                  value={assignEngineerId}
                  onChange={e => setAssignEngineerId(e.target.value)}
                  className="w-full px-3 py-2 border border-slate-300 rounded-md text-sm font-medium"
                >
                  <option value="">Select Supervising Engineer</option>
                  {engineers.map(eng => (
                    <option key={eng.id} value={eng.id}>
                      {eng.full_name} ({eng.role}) &bull; {eng.department}
                    </option>
                  ))}
                </select>
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-700 mb-1">Target Completion Date</label>
                <input
                  type="date"
                  value={targetDate}
                  onChange={e => setTargetDate(e.target.value)}
                  className="w-full px-3 py-2 border border-slate-300 rounded-md text-sm"
                  required
                />
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-700 mb-1">Directives / Inspection Guidelines</label>
                <textarea
                  rows={2}
                  value={assignRemarks}
                  onChange={e => setAssignRemarks(e.target.value)}
                  placeholder="Special instructions, safety precautions during high traffic..."
                  className="w-full px-3 py-2 border border-slate-300 rounded-md text-sm"
                />
              </div>

              <div className="flex justify-end gap-2 pt-2 border-t border-slate-100">
                <button
                  type="button"
                  onClick={() => setSelectedIssueForAssign(null)}
                  className="px-4 py-2 border border-slate-300 rounded-lg text-sm text-slate-700 hover:bg-slate-50 font-medium"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={assignIssueMutation.isPending}
                  className="px-5 py-2 bg-indigo-600 hover:bg-indigo-700 text-white rounded-lg text-sm font-semibold shadow-xs"
                >
                  {assignIssueMutation.isPending ? 'Delegating...' : 'Confirm Assignment'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Modal: Resolve Issue */}
      {selectedIssueForResolve && (
        <div className="fixed inset-0 bg-black/50 z-50 flex items-center justify-center p-4">
          <div className="bg-white rounded-xl max-w-md w-full p-6 space-y-4 shadow-2xl">
            <div className="flex justify-between items-center border-b border-slate-100 pb-3">
              <h3 className="text-lg font-bold text-slate-900 flex items-center gap-2">
                <span>✅</span> Mark Incident Resolved
              </h3>
              <button onClick={() => setSelectedIssueForResolve(null)} className="text-slate-400 hover:text-slate-600 text-lg">
                &times;
              </button>
            </div>

            <form onSubmit={handleResolveSubmit} className="space-y-4">
              <div>
                <label className="block text-xs font-semibold text-slate-700 mb-1">Resolution Status</label>
                <select
                  value={resolveStatus}
                  onChange={e => setResolveStatus(e.target.value)}
                  className="w-full px-3 py-2 border border-slate-300 rounded-md text-sm"
                >
                  <option value="RESOLVED">Resolved (Repairs / Actions Completed)</option>
                  <option value="CLOSED">Closed (Inspected & Found False Alarm / Non-Critical)</option>
                </select>
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-700 mb-1">Resolution Remarks</label>
                <textarea
                  rows={3}
                  value={resolveRemarks}
                  onChange={e => setResolveRemarks(e.target.value)}
                  placeholder="Detail completion notes, inspection confirmation..."
                  className="w-full px-3 py-2 border border-slate-300 rounded-md text-sm"
                  required
                />
              </div>

              <div className="flex justify-end gap-2 pt-2 border-t border-slate-100">
                <button
                  type="button"
                  onClick={() => setSelectedIssueForResolve(null)}
                  className="px-4 py-2 border border-slate-300 rounded-lg text-sm text-slate-700 hover:bg-slate-50 font-medium"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={resolveIssueMutation.isPending}
                  className="px-5 py-2 bg-emerald-600 hover:bg-emerald-700 text-white rounded-lg text-sm font-semibold shadow-xs"
                >
                  {resolveIssueMutation.isPending ? 'Updating...' : 'Save & Close Incident'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
