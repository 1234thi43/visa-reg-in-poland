import { NavLink, Outlet } from 'react-router-dom';
import { VFS_BOOKING_URL } from '../types';

const TABS = [
  { to: '/', label: 'Все' },
  { to: '/pinsk', label: 'Пинск' },
  { to: '/baranovichi', label: 'Барановичи' },
] as const;

export function Layout() {
  return (
    <div className="min-h-screen flex flex-col">
      <header className="border-b border-gray-800 bg-gray-900/80 backdrop-blur-sm sticky top-0 z-10">
        <div className="max-w-3xl mx-auto px-4 py-4">
          <div className="flex items-center justify-between mb-4">
            <div>
              <h1 className="text-xl font-bold text-white tracking-tight">
                VFS Poland — Мониторинг слотов
              </h1>
              <p className="text-sm text-gray-500 mt-0.5">Беларусь — Визовый центр Польши</p>
            </div>
            <a
              href={VFS_BOOKING_URL}
              target="_blank"
              rel="noopener noreferrer"
              className="text-sm text-blue-400 hover:text-blue-300 transition-colors"
            >
              Открыть VFS &rarr;
            </a>
          </div>

          <nav className="flex gap-1 bg-gray-800/50 rounded-lg p-1">
            {TABS.map(tab => (
              <NavLink
                key={tab.to}
                to={tab.to}
                end={tab.to === '/'}
                className={({ isActive }) =>
                  `flex-1 text-center py-2 px-4 rounded-md text-sm font-medium transition-all ${
                    isActive
                      ? 'bg-blue-600 text-white shadow-lg shadow-blue-600/20'
                      : 'text-gray-400 hover:text-gray-200 hover:bg-gray-700/50'
                  }`
                }
              >
                {tab.label}
              </NavLink>
            ))}
          </nav>
        </div>
      </header>

      <main className="flex-1 max-w-3xl mx-auto w-full px-4 py-6">
        <Outlet />
      </main>

      <footer className="border-t border-gray-800 py-3 text-center text-xs text-gray-600">
        Автоматическая проверка каждые 60 секунд
      </footer>
    </div>
  );
}
