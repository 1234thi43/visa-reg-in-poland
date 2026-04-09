import { useCallback, useEffect, useRef, useState } from 'react';
import type { CheckStatus, City, SlotInfo, SlotsResponse } from '../types';
import { fetchSlots } from '../services/api';
import { notifySlots, requestNotificationPermission } from '../services/notifications';

const POLL_INTERVAL = 15_000;

function toWsOrigin(origin: string): string {
  if (origin.startsWith('https://')) return `wss://${origin.slice('https://'.length)}`;
  if (origin.startsWith('http://')) return `ws://${origin.slice('http://'.length)}`;
  return origin;
}

export function useSlots(city?: City) {
  const [slots, setSlots] = useState<SlotInfo[]>([]);
  const [status, setStatus] = useState<CheckStatus>('idle');
  const [lastCheck, setLastCheck] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const prevSlotKeys = useRef<Set<string>>(new Set());

  const refresh = useCallback(async () => {
    try {
      const data: SlotsResponse = await fetchSlots(city);
      setSlots(data.slots);
      setStatus(data.status);
      setLastCheck(data.last_check);
      setError(null);

      const newKeys = new Set(data.slots.map(s => `${s.city}:${s.date}:${s.time}`));
      const freshSlots = data.slots.filter(
        s => !prevSlotKeys.current.has(`${s.city}:${s.date}:${s.time}`)
      );
      if (freshSlots.length > 0 && prevSlotKeys.current.size > 0) {
        notifySlots(freshSlots);
      }
      prevSlotKeys.current = newKeys;
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Ошибка загрузки');
    }
  }, [city]);

  useEffect(() => {
    requestNotificationPermission();
  }, []);

  useEffect(() => {
    refresh();
    const interval = setInterval(refresh, POLL_INTERVAL);
    return () => clearInterval(interval);
  }, [refresh]);

  useEffect(() => {
    const backendOrigin = (import.meta.env.VITE_BACKEND_ORIGIN as string | undefined)?.replace(/\/+$/, '');
    const wsUrl = backendOrigin
      ? `${toWsOrigin(backendOrigin)}/ws`
      : `${window.location.protocol === 'https:' ? 'wss:' : 'ws:'}//${window.location.host}/ws`;
    let ws: WebSocket | null = null;
    let reconnectTimer: ReturnType<typeof setTimeout>;

    function connect() {
      ws = new WebSocket(wsUrl);
      ws.onmessage = (event) => {
        try {
          const data: SlotsResponse = JSON.parse(event.data);
          const filtered = city
            ? data.slots.filter(s => s.city === city)
            : data.slots;
          setSlots(filtered);
          setStatus(data.status);
          setLastCheck(data.last_check);

          const newKeys = new Set(filtered.map(s => `${s.city}:${s.date}:${s.time}`));
          const freshSlots = filtered.filter(
            s => !prevSlotKeys.current.has(`${s.city}:${s.date}:${s.time}`)
          );
          if (freshSlots.length > 0 && prevSlotKeys.current.size > 0) {
            notifySlots(freshSlots);
          }
          prevSlotKeys.current = newKeys;
        } catch {
          // ignore parse errors
        }
      };
      ws.onclose = () => {
        reconnectTimer = setTimeout(connect, 5000);
      };
    }

    connect();
    return () => {
      ws?.close();
      clearTimeout(reconnectTimer);
    };
  }, [city]);

  return { slots, status, lastCheck, error, refresh };
}
