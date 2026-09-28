import client from './client';
import * as T from '../types';

export const api = {
  login: async (data: T.LoginRequest) => {
    // Standard OAuth2 form data
    const params = new URLSearchParams();
    params.append('username', data.username);
    params.append('password', data.password);
    const res = await client.post<T.LoginResponse>('/auth/login', params, {
      headers: { 'Content-Type': 'application/x-www-form-urlencoded' }
    });
    return res.data;
  },

  getBridges: async (params?: Record<string, any>) => {
    const res = await client.get<T.PaginatedResponse<T.BridgeListItem>>('/bridges', { params });
    return res.data;
  },

  getBridge: async (id: string) => {
    const res = await client.get<T.BridgeDetail>(`/bridges/${id}`);
    return res.data;
  },

  deleteBridge: async (id: string) => {
    const res = await client.delete(`/bridges/${id}`);
    return res.data;
  },

  getBridgeInspections: async (id: string) => {
    const res = await client.get<any>(`/bridges/${id}/inspections`);
    return Array.isArray(res.data) ? res.data : (res.data?.items || []);
  },

  createInspection: async (id: string, data: any) => {
    const res = await client.post(`/bridges/${id}/inspections`, data);
    return res.data;
  },

  getInspection: async (id: string) => {
    const res = await client.get<T.InspectionDetail>(`/inspections/${id}`);
    return res.data;
  },

  counterSignInspection: async (id: string, verification_remarks?: string) => {
    const res = await client.post(`/inspections/${id}/counter-sign`, { verification_remarks });
    return res.data;
  },

  getBridgeMaintenance: async (id: string) => {
    const res = await client.get<any>(`/bridges/${id}/maintenance`);
    return Array.isArray(res.data) ? res.data : (res.data?.items || []);
  },

  createMaintenance: async (id: string, data: any) => {
    const res = await client.post(`/bridges/${id}/maintenance`, data);
    return res.data;
  },

  updateMaintenanceStatus: async (id: string, payload: {
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
  }) => {
    const res = await client.put(`/maintenance/${id}/status`, payload);
    return res.data;
  },

  getBridgeLifecycle: async (id: string) => {
    const res = await client.get<any>(`/bridges/${id}/lifecycle`);
    return Array.isArray(res.data) ? res.data : (res.data?.items || []);
  },

  createLifecycleEvent: async (id: string, data: any) => {
    const res = await client.post(`/bridges/${id}/lifecycle`, data);
    return res.data;
  },

  getDashboardSummary: async (params?: Record<string, any>) => {
    const res = await client.get<T.DashboardSummary>('/dashboard/summary', { params });
    return res.data;
  },

  getPriorityList: async (params?: Record<string, any>) => {
    const res = await client.get<any>('/dashboard/priority-list', { params });
    return Array.isArray(res.data) ? res.data : (res.data?.items || []);
  },

  getGISBridges: async (params?: Record<string, any>) => {
    const res = await client.get<any>('/gis/bridges', { params });
    return Array.isArray(res.data) ? res.data : (res.data?.bridges || res.data?.items || []);
  },

  getAuditLogs: async (params?: Record<string, any>) => {
    const res = await client.get('/audit/logs', { params });
    return res.data;
  },

  // Distress Issues & Task Assignment
  getIssues: async (params?: Record<string, any>) => {
    const res = await client.get<T.DistressIssue[]>('/issues', { params });
    return res.data;
  },

  getBridgeIssues: async (bridgeId: string) => {
    const res = await client.get<T.DistressIssue[]>(`/bridges/${bridgeId}/issues`);
    return res.data;
  },

  createIssue: async (data: {
    bridge_id: string;
    source: string;
    issue_type: string;
    severity: string;
    description: string;
    location_details?: string;
    photo_url?: string;
  }) => {
    const res = await client.post<T.DistressIssue>('/issues', data);
    return res.data;
  },

  assignIssue: async (id: string, data: {
    assigned_inspector_id?: string;
    assigned_engineer_id?: string;
    target_completion_date?: string;
    remarks?: string;
  }) => {
    const res = await client.put<T.DistressIssue>(`/issues/${id}/assign`, data);
    return res.data;
  },

  resolveIssue: async (id: string, data: { status: string; remarks?: string }) => {
    const res = await client.put<T.DistressIssue>(`/issues/${id}/resolve`, data);
    return res.data;
  },

  getAssignableOfficers: async () => {
    const res = await client.get<{ inspectors: T.AssignableOfficer[]; engineers: T.AssignableOfficer[] }>('/issues/assignable-officers');
    return res.data;
  },
};
