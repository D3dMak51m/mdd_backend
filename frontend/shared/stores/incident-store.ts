// frontend/shared/stores/incident-store.ts
import {create} from 'zustand';
import {Incident} from '@/entities/incident/model';

export interface OnlineUser {
    id: number;
    full_name: string;
    email: string;
}

interface IncidentState {
    incidents: Map<string, Incident>;
    addOrUpdateIncident: (incident: Incident) => void;
    removeIncident: (uid: string) => void;
    activeIncidentId: string | null;
    setActiveIncidentId: (uid: string | null) => void;
    getSortedIncidents: () => Incident[];
    setIncidents: (incidents: Incident[]) => void;
    onlineUsers: OnlineUser[];
    setOnlineUsers: (users: OnlineUser[]) => void;
}

export const useIncidentStore = create<IncidentState>((set, get) => ({
    incidents: new Map(),
    activeIncidentId: null,

    addOrUpdateIncident: (incident) =>
        set((state) => {
            const newMap = new Map(state.incidents);
            newMap.set(incident.event_uid, incident);
            return {incidents: newMap};
        }),

    removeIncident: (uid) =>
        set((state) => {
            const newMap = new Map(state.incidents);
            newMap.delete(uid);
            return {incidents: newMap};
        }),

    setActiveIncidentId: (uid) => set({activeIncidentId: uid}),

    getSortedIncidents: () => {
        return Array.from(get().incidents.values()).sort(
            (a, b) => new Date(b.timestamp).getTime() - new Date(a.timestamp).getTime()
        );
    },

    // Реализация метода
    setIncidents: (data) => {
        const newMap = new Map();
        data.forEach((incident) => {
            // Используем event_uid как ключ, так как он уникален
            newMap.set(incident.event_uid, incident);
        });
        set({incidents: newMap});
    },
    onlineUsers: [],
    setOnlineUsers: (users) => set({onlineUsers: users}),
}));