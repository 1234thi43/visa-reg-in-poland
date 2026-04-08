import type { SlotInfo } from '../types';
import { VFS_BOOKING_URL } from '../types';

interface SlotCardProps {
  slot: SlotInfo;
}

export function SlotCard({ slot }: SlotCardProps) {
  return (
    <div className="rounded-xl border border-green-500/30 bg-green-500/5 p-4 transition-all hover:border-green-400/50 hover:bg-green-500/10">
      <div className="flex items-start justify-between gap-4">
        <div className="space-y-1">
          <div className="flex items-center gap-2">
            <span className="inline-block w-2 h-2 rounded-full bg-green-400 animate-pulse" />
            <span className="font-semibold text-green-300 text-lg">{slot.city}</span>
          </div>
          <div className="text-gray-200 text-base">
            <span className="font-mono">{slot.date}</span>
            {slot.time && (
              <span className="ml-2 text-blue-300 font-mono">{slot.time}</span>
            )}
          </div>
          {slot.details && (
            <p className="text-gray-400 text-sm">{slot.details}</p>
          )}
        </div>
        <a
          href={VFS_BOOKING_URL}
          target="_blank"
          rel="noopener noreferrer"
          className="shrink-0 rounded-lg bg-blue-600 px-4 py-2 text-sm font-medium text-white transition-colors hover:bg-blue-500 focus:outline-none focus:ring-2 focus:ring-blue-400"
        >
          Записаться
        </a>
      </div>
    </div>
  );
}
