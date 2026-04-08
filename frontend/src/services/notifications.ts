import type { SlotInfo } from '../types';
import { VFS_BOOKING_URL } from '../types';

let audioCtx: AudioContext | null = null;

function playAlertSound() {
  try {
    if (!audioCtx) audioCtx = new AudioContext();
    const osc = audioCtx.createOscillator();
    const gain = audioCtx.createGain();
    osc.connect(gain);
    gain.connect(audioCtx.destination);

    osc.type = 'sine';
    gain.gain.value = 0.3;

    const now = audioCtx.currentTime;
    [880, 1100, 880, 1100, 880].forEach((freq, i) => {
      osc.frequency.setValueAtTime(freq, now + i * 0.15);
    });

    osc.start(now);
    osc.stop(now + 0.75);
  } catch {
    // Audio not available
  }
}

export async function requestNotificationPermission(): Promise<boolean> {
  if (!('Notification' in window)) return false;
  if (Notification.permission === 'granted') return true;
  const result = await Notification.requestPermission();
  return result === 'granted';
}

export function notifySlots(slots: SlotInfo[]) {
  if (slots.length === 0) return;

  playAlertSound();

  if (Notification.permission !== 'granted') return;

  const cities = [...new Set(slots.map(s => s.city))];
  const title = `VFS: Найдены слоты! (${cities.join(', ')})`;
  const body = slots
    .slice(0, 5)
    .map(s => {
      let label = `${s.city}: ${s.date}`;
      if (s.time) label += ` ${s.time}`;
      return label;
    })
    .join('\n');

  const notification = new Notification(title, {
    body: body + `\n\nНажмите чтобы открыть`,
    icon: '🇵🇱',
    tag: 'vfs-slots',
    requireInteraction: true,
  });

  notification.onclick = () => {
    window.open(VFS_BOOKING_URL, '_blank');
    notification.close();
  };
}
