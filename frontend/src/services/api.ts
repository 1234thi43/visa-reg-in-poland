import type { SlotsResponse, StatusResponse } from '../types';

const BASE = '/api';

export async function fetchSlots(city?: string): Promise<SlotsResponse> {
  const url = city ? `${BASE}/slots/${encodeURIComponent(city)}` : `${BASE}/slots`;
  const res = await fetch(url);
  if (!res.ok) throw new Error(`HTTP ${res.status}`);
  return res.json();
}

export async function fetchStatus(): Promise<StatusResponse> {
  const res = await fetch(`${BASE}/status`);
  if (!res.ok) throw new Error(`HTTP ${res.status}`);
  return res.json();
}

export async function triggerCheck(): Promise<SlotsResponse> {
  const res = await fetch(`${BASE}/check-now`, { method: 'POST' });
  if (!res.ok) throw new Error(`HTTP ${res.status}`);
  return res.json();
}
