import { apiClient } from './client';

export interface DailyStats {
  id: number;
  date: string;
  total_incidents: number;
  resolved_count: number;
  false_alarms: number;
  avg_response_time_seconds: number;
  type_distribution: Record<string, number>;
}

export interface AuditLog {
  id: number;
  actor_name: string;
  actor_phone: string;
  action: string;
  target_model: string;
  target_id: string;
  changes: Record<string, any>;
  created_at: string;
}

export const analyticsApi = {
  getWeeklySummary: async () => {
    const { data } = await apiClient.get<DailyStats[]>('/analytics/weekly_summary/');
    return data;
  },

  getAuditLogs: async () => {
    const { data } = await apiClient.get<AuditLog[]>('/audit/');
    return data;
  }
};