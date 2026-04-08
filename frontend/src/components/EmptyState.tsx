interface EmptyStateProps {
  city?: string;
}

export function EmptyState({ city }: EmptyStateProps) {
  const label = city ?? 'выбранных городов';
  return (
    <div className="flex flex-col items-center justify-center py-20 text-center">
      <div className="text-5xl mb-4 opacity-50">📭</div>
      <h3 className="text-xl font-medium text-gray-400 mb-2">
        Свободных мест нет
      </h3>
      <p className="text-gray-500 max-w-sm">
        Для <span className="text-gray-300">{label}</span> сейчас нет доступных слотов.
        Мониторинг продолжается автоматически каждую минуту.
      </p>
    </div>
  );
}
