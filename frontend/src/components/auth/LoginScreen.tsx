import React, { useState } from 'react';
import { useApp } from '@/context/AppContext';
import { useTheme } from '@/context/ThemeContext';
import { authService } from '@/services/authService';
import { 
  Microscope, 
  Mail, 
  Lock, 
  Eye, 
  EyeOff, 
  ArrowRight, 
  Terminal, 
  Key, 
  Sun, 
  Moon,
  CheckCircle2
} from 'lucide-react';

export const LoginScreen: React.FC = () => {
  const { login } = useApp();
  const { theme, toggleTheme } = useTheme();

  const [email, setEmail] = useState('admin@testops.local');
  const [password, setPassword] = useState('admin123');
  const [showPassword, setShowPassword] = useState(false);
  const [remember, setRemember] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!email || !password) return;

    setError(null);
    setIsLoading(true);
    try {
      // Call real API to set JWT cookie
      await authService.login({ email, password });
      // Then update local app state
      login(email);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Login failed');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center p-4 relative bg-[var(--bg-main)]">
      {/* Top Right Theme Schema Switcher */}
      <div className="absolute top-4 right-4">
        <button
          onClick={toggleTheme}
          className="btn-outline px-3 py-1.5 text-xs flex items-center gap-2 font-mono shadow-xs"
        >
          {theme === 'light' ? <Moon className="w-4 h-4 text-[var(--color-brown)]" /> : <Sun className="w-4 h-4 text-[var(--color-orange)]" />}
          <span>{theme === 'light' ? 'Dark Schema' : 'Light Schema'}</span>
        </button>
      </div>

      <main className="w-full max-w-md space-y-6">
        {/* Branding & Header */}
        <div className="text-center space-y-2">
          <div className="inline-flex items-center justify-center w-14 h-14 rounded-xl bg-[var(--text-primary)] text-[var(--bg-card)] shadow-md mb-2">
            <Microscope className="w-8 h-8 text-[var(--color-matcha)]" />
          </div>
          <h1 className="text-2xl sm:text-3xl font-bold tracking-tight text-[var(--text-primary)]">
            TestOps Pro
          </h1>
          <p className="text-xs sm:text-sm text-[var(--text-muted)] font-mono">
            Precision QA & Business Operating System
          </p>
        </div>

        {/* Login Form Panel matching Screen 2 */}
        <div className="app-card p-6 sm:p-8 shadow-xl space-y-6 bg-[var(--bg-card)] border border-[var(--border-color)]">
          <form onSubmit={handleSubmit} className="space-y-4">
            {/* Email Field */}
            <div>
              <label className="block text-xs font-mono font-bold uppercase mb-1.5 text-[var(--text-secondary)]">
                Work Email
              </label>
              <div className="relative">
                <Mail className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-[var(--text-muted)]" />
                <input
                  type="email"
                  required
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  placeholder="name@company.com"
                  className="w-full pl-9 pr-4 py-2.5 bg-[var(--bg-card-alt)] border border-[var(--border-color)] rounded-lg text-sm text-[var(--text-primary)] focus:outline-none focus:ring-1 focus:ring-[var(--color-matcha)]"
                />
              </div>
            </div>

            {/* Password Field */}
            <div>
              <div className="flex justify-between items-center mb-1.5">
                <label className="block text-xs font-mono font-bold uppercase text-[var(--text-secondary)]">
                  Password
                </label>
                <a 
                  href="#" 
                  onClick={(e) => { e.preventDefault(); alert('Password reset link dispatched.'); }}
                  className="text-xs font-mono text-[var(--text-primary)] hover:underline font-semibold"
                >
                  Forgot?
                </a>
              </div>
              <div className="relative">
                <Lock className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-[var(--text-muted)]" />
                <input
                  type={showPassword ? 'text' : 'password'}
                  required
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  placeholder="••••••••"
                  className="w-full pl-9 pr-10 py-2.5 bg-[var(--bg-card-alt)] border border-[var(--border-color)] rounded-lg text-sm text-[var(--text-primary)] focus:outline-none focus:ring-1 focus:ring-[var(--color-matcha)]"
                />
                <button
                  type="button"
                  onClick={() => setShowPassword(!showPassword)}
                  className="absolute right-3 top-1/2 -translate-y-1/2 text-[var(--text-muted)] hover:text-[var(--text-primary)]"
                >
                  {showPassword ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
                </button>
              </div>
            </div>

            {/* Remember device */}
            <div className="flex items-center gap-2">
              <input
                type="checkbox"
                id="remember"
                checked={remember}
                onChange={(e) => setRemember(e.target.checked)}
                className="w-4 h-4 rounded border-[var(--border-color)] accent-[var(--color-matcha)] cursor-pointer"
              />
              <label htmlFor="remember" className="text-xs text-[var(--text-secondary)] cursor-pointer select-none">
                Remember this device for 30 days
              </label>
            </div>

            {/* Error message */}
            {error && (
              <div className="p-2.5 bg-[var(--color-dark-red-light)] border border-[var(--color-dark-red)] rounded text-xs text-[var(--color-dark-red)] font-mono" role="alert">
                {error}
              </div>
            )}

            {/* Sign In Submit */}
            <button
              type="submit"
              disabled={isLoading}
              className="w-full py-3 px-4 btn-matcha flex items-center justify-center gap-2 text-sm font-bold shadow-md disabled:opacity-50"
            >
              <span>{isLoading ? 'Signing in...' : 'Sign In'}</span>
              {!isLoading && <ArrowRight className="w-4 h-4" />}
            </button>
          </form>

          {/* Single Sign On Options */}
          <div className="space-y-4 pt-2">
            <div className="relative flex items-center justify-center">
              <div className="w-full border-t border-[var(--border-color)]" />
              <span className="bg-[var(--bg-card)] px-3 text-[10px] font-mono font-bold uppercase text-[var(--text-muted)] absolute">
                Or Continue With
              </span>
            </div>

            <div className="grid grid-cols-2 gap-3 pt-2">
              <button
                type="button"
                onClick={() => login('sso-engineer@company.com')}
                className="btn-outline py-2.5 px-3 flex items-center justify-center gap-2 text-xs font-mono"
              >
                <Terminal className="w-4 h-4 text-[var(--color-matcha)]" />
                <span>SSO</span>
              </button>
              <button
                type="button"
                onClick={() => login('okta-user@company.com')}
                className="btn-outline py-2.5 px-3 flex items-center justify-center gap-2 text-xs font-mono"
              >
                <Key className="w-4 h-4 text-[var(--color-orange)]" />
                <span>Okta</span>
              </button>
            </div>
          </div>
        </div>

        {/* Footer Account Prompt */}
        <p className="text-center text-xs text-[var(--text-secondary)]">
          New to TestOps?{' '}
          <a
            href="#"
            onClick={(e) => { e.preventDefault(); login('new-user@testops.io'); }}
            className="font-bold text-[var(--text-primary)] hover:underline"
          >
            Create an Account
          </a>
        </p>

        {/* System Status Footnote matching Screen 2 */}
        <div className="pt-4 flex items-center justify-center gap-3 opacity-70 text-[10px] font-mono font-bold uppercase text-[var(--text-muted)]">
          <span className="flex items-center gap-1.5">
            <CheckCircle2 className="w-3 h-3 text-[var(--color-matcha)]" /> SYSTEMS OPERATIONAL
          </span>
          <span>|</span>
          <span>V2.4.1 BUILD STABLE</span>
        </div>
      </main>
    </div>
  );
};
