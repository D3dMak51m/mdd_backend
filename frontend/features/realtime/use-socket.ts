import useWebSocket from 'react-use-websocket';
import { useEffect } from 'react';
import { useIncidentStore } from '@/shared/stores/incident-store';
import { WebSocketMessage } from '@/entities/incident/model';

export const useOpsSocket = () => {
  const { addOrUpdateIncident } = useIncidentStore();

  // Получаем хост для WS. В браузере это будет текущий хост (localhost:80 -> /ws/)
  // Nginx проксирует /ws/ на бэкенд
  const socketUrl = typeof window !== 'undefined'
    ? `${window.location.protocol === 'https:' ? 'wss' : 'ws'}://${window.location.host}/ws/sos_events/`
    : null;

  const { lastJsonMessage, readyState } = useWebSocket(socketUrl, {
    shouldReconnect: () => true,
    reconnectInterval: 3000,
    // Передаем токен (если бэкенд требует его в query params или headers,
    // но Django Channels AuthMiddlewareStack берет сессию из кук.
    // Если мы используем JWT, его нужно передать в protocols или query param.
    // Для простоты пока полагаемся на то, что Nginx прокидывает заголовки,
    // но обычно WS требует ?token=... если куки не работают)
  });

  useEffect(() => {
    if (lastJsonMessage) {
      const message = lastJsonMessage as WebSocketMessage;
      if (message.type === 'sos_event') {
        console.log('New Incident Received:', message.payload);
        addOrUpdateIncident(message.payload);

        // Звуковое оповещение
        try {
            const audio = new Audio('https://actions.google.com/sounds/v1/alarms/beep_short.ogg');
            audio.play();
        } catch (e) { console.error("Audio play failed", e); }
      }
    }
  }, [lastJsonMessage, addOrUpdateIncident]);

  return { readyState };
};