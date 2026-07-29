import React, { useState } from 'react';
import { useApp } from '@/context/AppContext';
import { 
  Plus, 
  Search, 
  ArrowRight, 
  Grid, 
  List,
} from 'lucide-react';

export const AllProjects: React.FC = () => {
  const { projects, setCurrentView } = useApp();
  const [filterEnv, setFilterEnv] = useState<string>('ALL');
  const [search, setSearch] = useState<string>('');
  const [layoutMode, setLayoutMode] = useState<'grid' | 'list'>('grid');

  const filteredProjects = projects.filter((p) => {
    const matchesEnv = filterEnv === 'ALL' || p.environment === filterEnv;
    const matchesSearch =
      !search ||
      p.name.toLowerCase().includes(search.toLowerCase()) ||
      p.subtitle.toLowerCase().includes(search.toLowerCase());
    return matchesEnv && matchesSearch;
  });

  return (
    <div className="space-y-6 pb-12">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-2 border-b border-[var(--border-color)]">
        <div>
          <h1 className="text-xl sm:text-2xl font-bold tracking-tight text-[var(--text-primary)]">
            All Projects & Workspaces
          </h1>
          <p className="text-xs sm:text-sm text-[var(--text-secondary)] mt-1">
            Manage test orchestration, environment bindings, and integration settings.
          </p>
        </div>
        <button
          onClick={() => setCurrentView('create-project')}
          className="btn-matcha px-4 py-2 text-xs font-mono font-bold flex items-center gap-2 shadow-sm shrink-0"
        >
          <Plus className="w-4 h-4" />
          <span>Create New Project</span>
        </button>
      </div>

      {/* Toolbar: Search, Env Filter & Grid/List toggle */}
      <div className="flex flex-wrap items-center justify-between gap-3 bg-[var(--bg-card)] p-3 border border-[var(--border-color)] rounded-lg">
        <div className="flex items-center gap-2">
          <div className="relative">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-[var(--text-muted)]" />
            <input
              type="text"
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              placeholder="Search projects..."
              className="pl-9 pr-3 py-1.5 bg-[var(--bg-card-alt)] border border-[var(--border-color)] rounded text-xs text-[var(--text-primary)] focus:outline-none focus:ring-1 focus:ring-[var(--color-matcha)] w-48 sm:w-64"
            />
          </div>

          <div className="flex items-center gap-1">
            {['ALL', 'Production', 'Staging', 'Dev'].map((env) => (
              <button
                key={env}
                onClick={() => setFilterEnv(env)}
                className={`px-2.5 py-1 text-xs font-mono rounded transition-colors ${
                  filterEnv === env
                    ? 'bg-[var(--text-primary)] text-[var(--bg-card)] font-bold'
                    : 'bg-[var(--bg-card-alt)] text-[var(--text-secondary)] hover:text-[var(--text-primary)]'
                }`}
              >
                {env}
              </button>
            ))}
          </div>
        </div>

        {/* Layout Toggle */}
        <div className="flex items-center gap-1 border border-[var(--border-color)] rounded p-0.5 bg-[var(--bg-card-alt)]">
          <button
            onClick={() => setLayoutMode('grid')}
            className={`p-1 rounded ${layoutMode === 'grid' ? 'bg-[var(--bg-card)] text-[var(--text-primary)] shadow-xs' : 'text-[var(--text-muted)]'}`}
            title="Grid Layout"
          >
            <Grid className="w-4 h-4" />
          </button>
          <button
            onClick={() => setLayoutMode('list')}
            className={`p-1 rounded ${layoutMode === 'list' ? 'bg-[var(--bg-card)] text-[var(--text-primary)] shadow-xs' : 'text-[var(--text-muted)]'}`}
            title="List Layout"
          >
            <List className="w-4 h-4" />
          </button>
        </div>
      </div>

      {/* Projects Display */}
      {layoutMode === 'grid' ? (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {filteredProjects.map((proj) => (
            <div
              key={proj.id}
              className="app-card p-5 flex flex-col justify-between hover:shadow-md transition-shadow relative overflow-hidden group"
            >
              <div
                className={`absolute top-0 left-0 right-0 h-1.5 ${
                  proj.status === 'ACTIVE'
                    ? 'bg-[var(--color-matcha)]'
                    : proj.status === 'CRITICAL'
                    ? 'bg-[var(--color-dark-red)]'
                    : 'bg-[var(--color-orange)]'
                }`}
              />

              <div>
                <div className="flex justify-between items-start mb-2 pt-1">
                  <div>
                    <h3 className="font-bold text-sm text-[var(--text-primary)]">{proj.name}</h3>
                    <p className="text-xs text-[var(--text-muted)] font-mono">{proj.subtitle}</p>
                  </div>
                  <span
                    className={`px-2 py-0.5 rounded text-[10px] font-mono font-bold ${
                      proj.status === 'ACTIVE'
                        ? 'badge-matcha'
                        : proj.status === 'CRITICAL'
                        ? 'badge-dark-red'
                        : 'badge-orange'
                    }`}
                  >
                    {proj.environment}
                  </span>
                </div>

                <div className="space-y-2 mt-4">
                  <div className="flex justify-between text-xs font-mono">
                    <span className="text-[var(--text-muted)]">Health Score</span>
                    <span className="font-bold text-[var(--text-primary)]">{proj.healthScore}%</span>
                  </div>

                  <div className="w-full bg-[var(--bg-card-alt)] h-1.5 rounded-full overflow-hidden flex">
                    <div className="bg-[var(--color-matcha)] h-full" style={{ width: `${proj.healthScore}%` }} />
                    <div
                      className="bg-[var(--color-dark-red)] h-full"
                      style={{ width: `${100 - proj.healthScore}%` }}
                    />
                  </div>
                </div>
              </div>

              <div className="pt-4 mt-4 border-t border-[var(--border-subtle)] flex items-center justify-between text-xs font-mono">
                <span className="text-[var(--text-muted)]">{proj.totalSuites} Test Suites</span>
                <button
                  onClick={() => setCurrentView('boards')}
                  className="text-[var(--text-primary)] hover:text-[var(--color-matcha)] transition-colors flex items-center gap-1 font-bold"
                >
                  <span>Open Board</span>
                  <ArrowRight className="w-3.5 h-3.5" />
                </button>
              </div>
            </div>
          ))}
        </div>
      ) : (
        <div className="app-card overflow-hidden">
          <table className="w-full text-left border-collapse min-w-[600px]">
            <thead>
              <tr className="bg-[var(--bg-card-alt)] text-[10px] font-mono font-bold uppercase text-[var(--text-muted)] border-b border-[var(--border-color)]">
                <th className="px-4 py-3">Project Name</th>
                <th className="px-4 py-3">Environment</th>
                <th className="px-4 py-3">Health Score</th>
                <th className="px-4 py-3">Status</th>
                <th className="px-4 py-3">Action</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-[var(--border-color)] text-xs font-mono">
              {filteredProjects.map((p) => (
                <tr key={p.id} className="hover:bg-[var(--bg-card-alt)] transition-colors">
                  <td className="px-4 py-3 font-sans">
                    <p className="font-bold text-[var(--text-primary)]">{p.name}</p>
                    <p className="text-[11px] text-[var(--text-muted)] font-mono">{p.subtitle}</p>
                  </td>
                  <td className="px-4 py-3">{p.environment}</td>
                  <td className="px-4 py-3 font-bold">{p.healthScore}%</td>
                  <td className="px-4 py-3">
                    <span
                      className={`px-2 py-0.5 rounded text-[10px] font-bold ${
                        p.status === 'ACTIVE'
                          ? 'badge-matcha'
                          : p.status === 'CRITICAL'
                          ? 'badge-dark-red'
                          : 'badge-orange'
                      }`}
                    >
                      {p.status}
                    </span>
                  </td>
                  <td className="px-4 py-3">
                    <button
                      onClick={() => setCurrentView('boards')}
                      className="px-2.5 py-1 btn-outline text-xs flex items-center gap-1"
                    >
                      <span>Board</span>
                      <ArrowRight className="w-3 h-3" />
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
};
