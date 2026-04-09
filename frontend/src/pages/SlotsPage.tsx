import type { City } from '../types';
import { useSlots } from '../hooks/useSlots';
import { StatusBadge } from '../components/StatusBadge';
import { SlotCard } from '../components/SlotCard';
import { EmptyState } from '../components/EmptyState';
import { triggerCheck, triggerTestNotification } from '../services/api';

interface SlotsPageProps {
  city?: City;
  title: string;
}

export function SlotsPage({ city, title }: SlotsPageProps) {
  const { slots, status, lastCheck, error, refresh } = useSlots(city);

  const handleManualCheck = async () => {
    try {
      await triggerCheck();
      await refresh();
    } catch {
      // handled by hook
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-lg font-semibold text-white">{title}</h2>
          {slots.length > 0 && (
            <p className="text-sm text-green-400 mt-1">
              Найдено мест: {slots.length}
            </p>
          )}
        </div>
        <div className="flex gap-2">
          <button
            onClick={() => triggerTestNotification()}
            className="rounded-lg bg-yellow-600/20 border border-yellow-600/40 px-4 py-2 text-sm text-yellow-300 transition-all hover:bg-yellow-600/30 hover:text-yellow-200"
          >
            Тест уведомлений
          </button>
          <button
            onClick={handleManualCheck}
            disabled={status === 'checking'}
            className="rounded-lg bg-gray-800 border border-gray-700 px-4 py-2 text-sm text-gray-300 transition-all hover:bg-gray-700 hover:text-white disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {status === 'checking' ? 'Проверяю...' : 'Проверить сейчас'}
          </button>
        </div>
      </div>

      <StatusBadge status={status} lastCheck={lastCheck} />

      {error && (
        <div className="rounded-lg border border-red-500/30 bg-red-500/10 p-4 text-sm text-red-300">
          {error}
        </div>
      )}

      {status === 'waiting_for_auth' && (
        <div className="rounded-lg border border-yellow-500/30 bg-yellow-500/10 p-4 text-sm text-yellow-300">
          <p className="font-medium mb-1">Требуется авторизация</p>
          <p className="text-yellow-400/70">
            Пожалуйста, пройдите авторизацию в открывшемся окне браузера.
            После этого мониторинг начнётся автоматически.
          </p>
        </div>
      )}

      {slots.length > 0 ? (
        <div className="space-y-3">
          {slots.map((slot, i) => (
            <SlotCard key={`${slot.city}-${slot.date}-${slot.time}-${i}`} slot={slot} />
          ))}
        </div>
      ) : (
        status !== 'waiting_for_auth' && <EmptyState city={city} />
      )}
    </div>
  );
}
