// Auth
export interface LoginRequest { username: string; password: string; }
export interface LoginResponse {
  access_token: string;
  token_type: string;
  user: UserInfo;
}
export interface UserInfo {
  id: string;
  username: string;
  full_name: string;
  email: string;
  department: string;
  role: string;
  permissions: string[];
}

// Bridge
export interface BridgeListItem {
  bridge_id: string;
  bridge_code: string;
  bridge_name: string;
  asset_type?: string;
  bridge_type: string;
  structure_category: string;
  current_status: string;
  year_constructed: number;
  district: string;
  state: string;
  latitude: number;
  longitude: number;
  latest_health_index: number | null;
  latest_condition_category: string | null;
  road_name: string;
}

export interface BridgeLocation {
  state: string;
  district: string;
  taluka: string | null;
  village_or_city: string | null;
  latitude: number;
  longitude: number;
  elevation: number | null;
  chainage_start: number | null;
  chainage_end: number | null;
}

export interface BridgeEngineering {
  total_length: number | null;
  carriageway_width: number | null;
  deck_width?: number | null;
  overall_width: number | null;
  number_of_lanes: number | null;
  number_of_spans: number | null;
  superstructure_type: string | null;
  substructure_type: string | null;
  foundation_type: string | null;
  construction_material: string | null;
  deck_material: string | null;
  design_loading: string | null;
  design_speed: number | null;
  design_life: number | null;
  // Multi-asset engineering specs
  tunnel_type?: string | null;
  bore_diameter?: number | null;
  ventilation_system?: string | null;
  pavement_type?: string | null;
  culvert_type?: string | null;
  opening_span?: number | null;
  clear_height?: number | null;
}

export interface ConditionSummary {
  overall_health_index: number;
  condition_category: string;
  structural_score: number;
  functional_score: number;
  safety_score: number;
  assessment_date: string;
  calculation_version: string;
}

export interface InspectionSummary {
  inspection_id: string;
  inspection_type: string;
  inspection_date: string;
  overall_condition: string;
  next_inspection_date: string | null;
  photo_evidence_url?: string | null;
  geofence_verified?: boolean;
  geofence_distance_meters?: number | null;
  counter_signed_by_name?: string | null;
}

export interface MaintenanceRecord {
  maintenance_id: string;
  maintenance_type: string;
  issue_description: string;
  status: string; // REPORTED, ESTIMATED, SANCTIONED, TENDER_AWARDED, IN_PROGRESS, COMPLETED, VERIFIED, CANCELLED
  priority: string;
  reported_date: string;
  start_date: string | null;
  completion_date: string | null;
  estimated_cost: number | null;
  actual_cost: number | null;
  // Indian Government Procurement & Sanction Tracking
  estimated_by_name?: string | null;
  sanction_number?: string | null;
  sanctioned_amount?: number | null;
  approved_by_name?: string | null;
  tender_number?: string | null;
  work_order_number?: string | null;
  tender_value?: number | null;
  assigned_contractor?: string | null;
  verified_by_name?: string | null;
  verification_notes?: string | null;
}

export interface BridgeDetail {
  bridge_id: string;
  bridge_code: string;
  bridge_name: string;
  asset_type?: string;
  bridge_type: string;
  structure_category: string;
  current_status: string;
  department: string | null;
  owning_authority: string | null;
  maintaining_authority: string | null;
  road_name: string | null;
  route_number: string | null;
  year_constructed: number | null;
  date_commissioned: string | null;
  traffic_status: string | null;
  daily_traffic_estimate: number | null;
  load_restriction: string | null;
  speed_restriction: number | null;
  description: string | null;
  created_at: string;
  updated_at: string;
  location: BridgeLocation;
  engineering: BridgeEngineering;
  latest_condition: ConditionSummary | null;
  latest_inspection: InspectionSummary | null;
  active_maintenance: MaintenanceRecord[];
}

// Inspection detail
export interface InspectionComponent {
  component_id: string;
  component_type: string;
  condition_rating: number;
  observations: string | null;
  recommendation: string | null;
}

export interface Defect {
  defect_id: string;
  defect_type: string;
  severity: string;
  component_type: string | null;
  location_on_bridge: string | null;
  description: string | null;
  immediate_action_required: boolean;
  status: string;
}

export interface InspectionDetail {
  inspection_id: string;
  bridge_id: string;
  inspection_type: string;
  inspection_date: string;
  inspector_name: string | null;
  weather_condition: string | null;
  overall_condition: string;
  findings: string | null;
  recommendations: string | null;
  next_inspection_date: string | null;
  inspection_status: string;
  photo_evidence_url?: string | null;
  geofence_verified?: boolean;
  geofence_distance_meters?: number | null;
  inspector_gps_latitude?: number | null;
  inspector_gps_longitude?: number | null;
  counter_signed_by?: string | null;
  counter_signed_by_name?: string | null;
  counter_signed_at?: string | null;
  verification_remarks?: string | null;
  components: InspectionComponent[];
  defects: Defect[];
  condition_assessment: ConditionSummary | null;
}

// Distress Issues & Task Assignment
export interface DistressIssue {
  id: string;
  bridge_id: string;
  bridge_code?: string;
  bridge_name?: string;
  asset_type?: string;
  district?: string;
  reported_by: string;
  reporter_name?: string;
  reporter_role?: string;
  source: string; // FIELD_INSPECTION, CITIZEN_REPORT, SENSOR_BHI_ALERT
  issue_type: string;
  severity: string; // LOW, MEDIUM, HIGH, CRITICAL
  description: string;
  location_details?: string | null;
  photo_url?: string | null;
  status: string; // REPORTED, ASSIGNED, UNDER_INSPECTION, RESOLVED, CLOSED
  assigned_inspector_id?: string | null;
  assigned_inspector_name?: string | null;
  assigned_engineer_id?: string | null;
  assigned_engineer_name?: string | null;
  target_completion_date?: string | null;
  created_at: string;
  updated_at: string;
}

export interface AssignableOfficer {
  id: string;
  full_name: string;
  role: string;
  department: string;
}

// Lifecycle
export interface LifecycleEvent {
  event_id: string;
  event_type: string;
  event_date: string;
  performed_by_name: string | null;
  department: string | null;
  description: string | null;
  previous_status: string | null;
  new_status: string | null;
  remarks: string | null;
  created_at: string;
}

// Dashboard
export interface DashboardSummary {
  total_bridges: number;
  total_assets?: number;
  by_asset_type?: Record<string, number>;
  by_status: Record<string, number>;
  by_condition: Record<string, number>;
  critical_bridges_count: number;
  overdue_inspections_count: number;
  recent_events: Array<{
    event_id: string;
    bridge_code: string;
    bridge_name: string;
    asset_type?: string;
    event_type: string;
    event_date: string;
    description: string;
  }>;
}

export interface PriorityItem {
  bridge_id: string;
  bridge_code: string;
  bridge_name: string;
  asset_type?: string;
  health_index: number;
  condition_category: string;
  priority: string;
  priority_score: number;
  reasons: string[];
  district: string;
  current_status: string;
}

// GIS
export interface GISBridge {
  bridge_id: string;
  bridge_code: string;
  bridge_name: string;
  asset_type?: string;
  latitude: number;
  longitude: number;
  current_status: string;
  condition_category: string | null;
  health_index: number | null;
  bridge_type: string;
  district: string;
  year_constructed: number | null;
}

// Common
export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  page: number;
  limit: number;
}
