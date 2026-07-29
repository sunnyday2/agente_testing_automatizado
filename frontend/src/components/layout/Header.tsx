import React, { useState } from 'react';
import { useApp } from '@/context/AppContext';
import { useTheme } from '@/context/ThemeContext';
import { AppView } from '@/types';
import { 
  Sun, 
  Moon, 
  Search, 
  Bell, 
  HelpCircle, 
  Settings, 
  LogOut, 
  FlaskConical,
  X,
  CheckCircle2,
  AlertTriangle,
  Info
} from 'lucide-react';

export const Header: React.FC = () => {
  const { currentView, setCurrentView, user, logout, searchQuery, setSearchQuery, events } = useApp();
  const { theme, toggleTheme } = useTheme();
  const [showNotifications, setShowNotifications] = useState(false);
  const [showUserMenu, setShowUserMenu] = useState(false);

  const navItems: { id: AppView; label: string }[] = [
    { id: 'projects', label: 'Projects' },
    { id: 'boards', label: 'Boards' },
    { id: 'tests', label: 'Tests' },
    { id: 'reports', label: 'Results' },
  ];

  return (
    <header className="app-header fixed top-0 left-0 right-0 z-50 h-16 px-4 md:px-6 flex items-center justify-between">
      {/* Brand Logo & Top Navigation */}
      <div className="flex items-center gap-6 lg:gap-8">
        <button 
          onClick={() => setCurrentView('overview')} 
          className="flex items-center gap-2 text-left focus:outline-none group"
        >
          <div className="w-9 h-9 rounded-lg bg-[var(--text-primary)] text-[var(--bg-card)] flex items-center justify-center transition-transform group-hover:scale-105">
            <FlaskConical className="w-5 h-5" />
          </div>
          <div>
            <span className="font-bold text-lg md:text-xl tracking-tight text-[var(--text-primary)] block leading-none">
              TestOps Pro
            </span>
            <span className="text-[10px] font-mono uppercase tracking-wider text-[var(--text-muted)] hidden sm:block">
              Business OS
            </span>
          </div>
        </button>

        {/* Top Navigation Links */}
        <nav className="hidden md:flex gap-1 h-16 items-center">
          {navItems.map(item => {
            const isActive = currentView === item.id || (item.id === 'projects' && currentView === 'all-projects' as any);
            return (
              <button
                key={item.id}
                onClick={() => setCurrentView(item.id)}
                className={`px-3 py-1.5 text-sm font-medium rounded-md transition-colors relative ${
                  isActive
                    ? 'text-[var(--text-primary)] font-semibold bg-[var(--bg-card-alt)]'
                    : 'text-[var(--text-secondary)] hover:text-[var(--text-primary)] hover:bg-[var(--bg-card-alt)]'
                }`}
              >
                {item.label}
                {isActive && (
                  <span className="absolute bottom-0 left-2 right-2 h-0.5 bg-[var(--color-matcha)] rounded-full" />
                )}
              </button>
            );
          })}
        </nav>
      </div>

      {/* Global Search & Action Controls */}
      <div className="flex items-center gap-2 sm:gap-3">
        {/* Search Bar */}
        <div className="relative hidden sm:block">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-[var(--text-muted)]" />
          <input
            type="text"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            placeholder="Search workspace, issues, suites..."
            className="pl-9 pr-4 py-1.5 bg-[var(--bg-card-alt)] border border-[var(--border-color)] rounded-md text-xs sm:text-sm text-[var(--text-primary)] placeholder-[var(--text-muted)] focus:outline-none focus:ring-1 focus:ring-[var(--color-matcha)] w-48 lg:w-64 transition-all"
          />
          {searchQuery && (
            <button 
              onClick={() => setSearchQuery('')}
              className="absolute right-2.5 top-1/2 -translate-y-1/2 text-[var(--text-muted)] hover:text-[var(--text-primary)]"
            >
              <X className="w-3.5 h-3.5" />
            </button>
          )}
        </div>

        {/* Theme Schema Switcher (Light / Dark) */}
        <button
          onClick={toggleTheme}
          title={`Switch to ${theme === 'light' ? 'Dark' : 'Light'} Schema`}
          className="p-2 text-[var(--text-secondary)] hover:text-[var(--text-primary)] hover:bg-[var(--bg-card-alt)] rounded-md transition-colors flex items-center gap-1.5"
          id="theme-toggle-btn"
        >
          {theme === 'light' ? (
            <Moon className="w-4 h-4 text-[var(--color-brown)]" />
          ) : (
            <Sun className="w-4 h-4 text-[var(--color-orange)]" />
          )}
          <span className="text-xs font-mono font-medium hidden xl:inline uppercase">
            {theme === 'light' ? 'Light' : 'Dark'}
          </span>
        </button>

        {/* Notifications Icon & Dropdown */}
        <div className="relative">
          <button
            onClick={() => setShowNotifications(!showNotifications)}
            className="p-2 text-[var(--text-secondary)] hover:text-[var(--text-primary)] hover:bg-[var(--bg-card-alt)] rounded-md transition-colors relative"
            title="Notifications"
          >
            <Bell className="w-4 h-4" />
            <span className="absolute top-1.5 right-1.5 w-2 h-2 rounded-full bg-[var(--color-dark-red)]" />
          </button>

          {showNotifications && (
            <div className="absolute right-0 mt-2 w-80 sm:w-96 app-card shadow-lg p-4 z-50">
              <div className="flex items-center justify-between pb-3 border-b border-[var(--border-color)]">
                <h4 className="font-semibold text-sm">System Audit Stream</h4>
                <button 
                  onClick={() => setShowNotifications(false)}
                  className="text-[var(--text-muted)] hover:text-[var(--text-primary)]"
                >
                  <X className="w-4 h-4" />
                </button>
              </div>
              <div className="space-y-3 mt-3 max-h-72 overflow-y-auto custom-scrollbar pr-1">
                {events.map((evt) => (
                  <div key={evt.id} className="p-2.5 rounded bg-[var(--bg-card-alt)] flex items-start gap-2.5 text-xs">
                    {evt.type === 'success' && <CheckCircle2 className="w-4 h-4 text-[var(--color-matcha)] shrink-0 mt-0.5" />}
                    {evt.type === 'error' && <AlertTriangle className="w-4 h-4 text-[var(--color-dark-red)] shrink-0 mt-0.5" />}
                    {evt.type === 'info' && <Info className="w-4 h-4 text-[var(--color-orange)] shrink-0 mt-0.5" />}
                    <div className="flex-1">
                      <p className="font-semibold text-[var(--text-primary)]">{evt.title}</p>
                      <p className="text-[var(--text-secondary)] mt-0.5">{evt.description}</p>
                      <span className="text-[10px] text-[var(--text-muted)] font-mono block mt-1">{evt.timestamp}</span>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>

        {/* Support & Settings Icons */}
        <button
          onClick={() => setCurrentView('reports')}
          className="p-2 text-[var(--text-secondary)] hover:text-[var(--text-primary)] hover:bg-[var(--bg-card-alt)] rounded-md transition-colors hidden sm:block"
          title="Help & Support"
        >
          <HelpCircle className="w-4 h-4" />
        </button>

        <button
          onClick={() => setCurrentView('settings')}
          className="p-2 text-[var(--text-secondary)] hover:text-[var(--text-primary)] hover:bg-[var(--bg-card-alt)] rounded-md transition-colors hidden sm:block"
          title="Settings"
        >
          <Settings className="w-4 h-4" />
        </button>

        {/* User Profile Avatar / Logout Dropdown */}
        <div className="relative ml-1">
          <button
            onClick={() => setShowUserMenu(!showUserMenu)}
            className="flex items-center gap-2 p-1 rounded-full border border-[var(--border-color)] hover:border-[var(--text-secondary)] transition-colors"
          >
            <img
              src={user.avatar}
              alt={user.name}
              className="w-7 h-7 rounded-full object-cover"
            />
          </button>

          {showUserMenu && (
            <div className="absolute right-0 mt-2 w-56 app-card shadow-xl p-3 z-50">
              <div className="pb-2 mb-2 border-b border-[var(--border-color)]">
                <p className="font-bold text-xs text-[var(--text-primary)]">{user.name}</p>
                <p className="text-[11px] text-[var(--text-muted)] font-mono">{user.email}</p>
                <span className="inline-block px-1.5 py-0.5 mt-1 text-[10px] rounded font-mono badge-matcha">
                  {user.role}
                </span>
              </div>

              <div className="space-y-1">
                <button
                  onClick={() => {
                    setCurrentView('settings');
                    setShowUserMenu(false);
                  }}
                  className="w-full text-left px-2 py-1.5 text-xs text-[var(--text-secondary)] hover:text-[var(--text-primary)] hover:bg-[var(--bg-card-alt)] rounded transition-colors flex items-center gap-2"
                >
                  <Settings className="w-3.5 h-3.5" /> Workspace Settings
                </button>
                <button
                  onClick={() => {
                    logout();
                    setShowUserMenu(false);
                  }}
                  className="w-full text-left px-2 py-1.5 text-xs text-[var(--color-dark-red)] hover:bg-[var(--color-dark-red-light)] rounded transition-colors flex items-center gap-2 font-medium"
                >
                  <LogOut className="w-3.5 h-3.5" /> Sign Out
                </button>
              </div>
            </div>
          )}
        </div>
      </div>
    </header>
  );
};
