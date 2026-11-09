import { apiClient } from './client';
import { Incident } from '@/entities/incident/model';

export const incidentApi = {
  // Получить список (активные)
  getActive: async () => {
    const { data } = await apiClient.get<Incident[]>('/sos/?active=true');
    return data;
  },

  // Принять вызов (I am coming)
  respond: async (uid: string) => {
    const { data } = await apiClient.post(`/sos/${uid}/respond/`, {
      status: 'ACCEPTED'
    });
    return data;
  },

  // Завершить инцидент
  resolve: async (uid: string, notes: string) => {
    const { data } = await apiClient.post(`/sos/${uid}/resolve/`, {
      notes
    });
    return data;
  }
};