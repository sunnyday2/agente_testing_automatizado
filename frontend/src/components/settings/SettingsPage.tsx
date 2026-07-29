import React, { useState } from 'react';
import { useTheme } from '@/context/ThemeContext';
import { useApp } from '@/context/AppContext';
import { 
  Sun, 
  Moon, 
  Check, 
  Palette, 
  Bell, 
  ShieldCheck, 
  Key, 
  Save,
  CheckCircle2
} from 'lucide-react';

export const SettingsPage: React.FC = () => {
  const { theme, setTheme } = useTheme();
  const { user } = useApp();

  const [slackWebhook, setSlackWebhook] = useState('https://hooks.slack.com/services/T00/B00/XXXXX');
  const [emailAlerts, setEmailAlerts] = useState(true);
  const [apiKey, setApiKey] = useState('tp_live_9f82a10b429c41d7e8281a');
  const [savedSuccess, setSavedSuccess] = useState(false);

  const colorSwatches = [
    { name: 'White', colorClass: 'bg-white border border-gray-300 text-black', hex: '#FFFFFF' },
    { name: 'Matcha Green', colorClass: 'bg-[var(--color-matcha)] text-white', hex: '#4F772D' },
    { name: 'Dark Red', colorClass: 'bg-[var(--color-dark-red)] text-white', hex: '#8B0000' },
    { name: 'Orange', colorClass: 'bg-[var(--color-orange)] text-white', hex: '#D97706' },
    { name: 'Okra / Ochre', colorClass: 'bg-[var(--color-okra)] text-white', hex: '#656D4A' },
    { name: 'Brown', colorClass: 'bg-[var(--color-brown)] text-white', hex: '#5C4033' },
    { name: 'Dirty White', colorClass: 'bg-[var(--color-dirty-white)] text-black border border-gray-300', hex: '#F4F3EF' },
    { name: 'Light Green', colorClass: 'bg-[var(--color-light-green)] text-black', hex: '#90A955' },
    { name: 'Black', colorClass: 'bg-[var(--color-black)] text-white', hex: '#0A0A0A' },
  ];

  const handleSave = () => {
    setSavedSuccess(true);
    setTimeout(() => setSavedSuccess(false), 2500);
  };

  return (
    <div className="max-w-4xl mx-auto space-y-6 pb-12">
      {/* Header */}
      <div className="pb-2 border-b border-[var(--border-color)]">
        <h1 className="text-xl sm:text-2xl font-bold tracking-tight text-[var(--text-primary)]">
          Workspace Settings & Color Schema
        </h1>
        <p className="text-xs sm:text-sm text-[var(--text-secondary)] mt-1">
          Customize light and dark appearance, audit color tokens, and configure webhook credentials.
        </p>
      </div>

      {/* Theme Schema Selector */}
      <section className="app-card overflow-hidden">
        <div className="p-4 bg-[var(--bg-card-alt)] border-b border-[var(--border-color)] flex items-center justify-between">
          <div className="flex items-center gap-2">
            <Palette className="w-4 h-4 text-[var(--color-matcha)]" />
            <h2 className="font-bold text-sm text-[var(--text-primary)]">Theme Schema Mode</h2>
          </div>
          <span className="text-xs font-mono font-bold uppercase text-[var(--text-muted)]">
            CURRENT: {theme.toUpperCase()} SCHEMA
          </span>
        </div>

        <div className="p-6 space-y-6">
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            {/* Light Schema Card */}
            <div
              onClick={() => setTheme('light')}
              className={`p-4 rounded-lg border-2 cursor-pointer transition-all ${
                theme === 'light'
                  ? 'border-[var(--color-matcha)] bg-white text-black shadow-md'
                  : 'border-[var(--border-color)] bg-[#f4f3ef] text-gray-700 hover:border-gray-400'
              }`}
            >
              <div className="flex items-center justify-between mb-3">
                <div className="flex items-center gap-2">
                  <Sun className="w-5 h-5 text-amber-600" />
                  <span className="font-bold text-sm">Light Schema</span>
                </div>
                {theme === 'light' && <Check className="w-5 h-5 text-[var(--color-matcha)]" />}
              </div>
              <p className="text-xs text-gray-600">
                Warm off-white background with high-contrast slate typography and matcha/okra accents.
              </p>
            </div>

            {/* Dark Schema Card */}
            <div
              onClick={() => setTheme('dark')}
              className={`p-4 rounded-lg border-2 cursor-pointer transition-all ${
                theme === 'dark'
                  ? 'border-[var(--color-matcha)] bg-[#141614] text-[#f4f3ef] shadow-md'
                  : 'border-[var(--border-color)] bg-[#1e201d] text-gray-300 hover:border-gray-500'
              }`}
            >
              <div className="flex items-center justify-between mb-3">
                <div className="flex items-center gap-2">
                  <Moon className="w-5 h-5 text-orange-400" />
                  <span className="font-bold text-sm">Dark Schema</span>
                </div>
                {theme === 'dark' && <Check className="w-5 h-5 text-[var(--color-matcha)]" />}
              </div>
              <p className="text-xs text-gray-400">
                Dark charcoal background with dirty-white typography and low-strain status indicators.
              </p>
            </div>
          </div>

          {/* Color Palette Audit Grid */}
          <div className="pt-2 border-t border-[var(--border-color)] space-y-3">
            <h3 className="text-xs font-mono font-bold uppercase text-[var(--text-muted)]">
              Strict Approved Color Swatch Token Palette
            </h3>
            <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-5 gap-2.5">
              {colorSwatches.map((s) => (
                <div
                  key={s.name}
                  className={`p-2.5 rounded-md text-xs font-mono font-semibold flex flex-col justify-between h-16 shadow-xs ${s.colorClass}`}
                >
                  <span className="text-[10px] uppercase font-bold leading-none">{s.name}</span>
                  <span className="text-[10px] opacity-80">{s.hex}</span>
                </div>
              ))}
            </div>
          </div>
        </div>
      </section>

      {/* Webhook & Notification Settings */}
      <section className="app-card overflow-hidden">
        <div className="p-4 bg-[var(--bg-card-alt)] border-b border-[var(--border-color)] flex items-center gap-2">
          <Bell className="w-4 h-4 text-[var(--color-orange)]" />
          <h2 className="font-bold text-sm text-[var(--text-primary)]">Webhook Alerts & Notifications</h2>
        </div>

        <div className="p-6 space-y-4">
          <div>
            <label className="block text-xs font-mono font-bold uppercase mb-1">
              Slack Incoming Webhook URL
            </label>
            <input
              type="text"
              value={slackWebhook}
              onChange={(e) => setSlackWebhook(e.target.value)}
              className="w-full px-3 py-2 bg-[var(--bg-card-alt)] border border-[var(--border-color)] rounded text-xs font-mono text-[var(--text-primary)] focus:outline-none focus:ring-1 focus:ring-[var(--color-matcha)]"
            />
          </div>

          <div className="flex items-center gap-3 pt-2">
            <input
              type="checkbox"
              id="emailAlerts"
              checked={emailAlerts}
              onChange={(e) => setEmailAlerts(e.target.checked)}
              className="w-4 h-4 rounded border-[var(--border-color)] accent-[var(--color-matcha)] cursor-pointer"
            />
            <label htmlFor="emailAlerts" className="text-xs font-medium cursor-pointer">
              Dispatch email notification on critical test suite regressions
            </label>
          </div>
        </div>
      </section>

      {/* API Key Credentials */}
      <section className="app-card overflow-hidden">
        <div className="p-4 bg-[var(--bg-card-alt)] border-b border-[var(--border-color)] flex items-center gap-2">
          <Key className="w-4 h-4 text-[var(--color-okra)]" />
          <h2 className="font-bold text-sm text-[var(--text-primary)]">API Access Credentials</h2>
        </div>

        <div className="p-6 space-y-4">
          <div>
            <label className="block text-xs font-mono font-bold uppercase mb-1">
              Secret Workspace Key
            </label>
            <div className="flex gap-2">
              <input
                type="text"
                readOnly
                value={apiKey}
                className="flex-1 px-3 py-2 bg-[var(--bg-card-alt)] border border-[var(--border-color)] rounded text-xs font-mono text-[var(--text-primary)]"
              />
              <button
                onClick={() => alert('API Key copied to clipboard!')}
                className="btn-outline px-3 py-2 text-xs font-mono"
              >
                Copy
              </button>
            </div>
          </div>
        </div>
      </section>

      {/* Save Button */}
      <div className="flex items-center justify-between pt-2">
        {savedSuccess ? (
          <span className="text-xs font-mono font-bold text-[var(--color-matcha)] flex items-center gap-1">
            <CheckCircle2 className="w-4 h-4" /> Preferences saved successfully!
          </span>
        ) : <div />}

        <button
          onClick={handleSave}
          className="btn-matcha px-6 py-2.5 text-xs font-mono font-bold flex items-center gap-2 shadow-md"
        >
          <Save className="w-4 h-4" /> Save Preferences
        </button>
      </div>
    </div>
  );
};
