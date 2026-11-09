export interface Incident {
  id: number;
  event_uid: string;
  status: 'NEW' | 'IN_PROGRESS' | 'RESOLVED';
  timestamp: string;
  detected_type: string;
  severity: number;
  lat: number;
  lon: number;
  user: {
    full_name: string;
    phone_number: string;
  };
  device: {
    device_uid: string;
    model: string;
    battery_level: number;
  };
}

export interface WebSocketMessage {
  type: string;
  payload: Incident;
}