import type { CheckStatus } from '../types';

const STATUS_CONFIG: Record<CheckStatus, { label: string; color: string; pulse: boolean }> = {
  idle: { label: 'Ожидание', color: 'bg-gray-500', pulse: false },
  checking: { label: 'Проверка...', color: 'bg-blue-500', pulse: true },
  waiting_for_auth: { label: 'Ожидание авторизации', color: 'bg-yellow-500', pulse: true },
  ok: { label: 'Активен', color: 'bg-green-500', pulse: false },
  error: { label: 'Ошибка', color: 'bg-red-500', pulse: false },
};

interface StatusBadgeProps {
  status: CheckStatus;
  lastCheck: string | null;
}

export function StatusBadge({ status, lastCheck }: StatusBadgeProps) {
  const config = STATUS_CONFIG[status];
  const formattedTime = lastCheck
    ? new Date(lastCheck).toLocaleTimeString('ru-RU')
    : '—';

  return (
    <div className="flex items-center gap-3 text-sm">
      <span className="flex items-center gap-2">
        <span className={`inline-block w-2.5 h-2.5 rounded-full ${config.color} ${config.pulse ? 'animate-pulse' : ''}`} />
        <span className="text-gray-300">{config.label}</span>
      </span>
      <span className="text-gray-500">
        Последняя проверка: {formattedTime}
      </span>
    </div>
  );
}
