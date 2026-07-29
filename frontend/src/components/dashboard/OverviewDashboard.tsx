import React from 'react';
import { useApp } from '@/context/AppContext';
import { useStats } from '@/hooks/useStats';
import { 
  Calendar, 
  Download, 
  CheckCircle2, 
  AlertCircle, 
  Clock, 
  Play, 
  ArrowRight, 
  Plus, 
  TrendingUp, 
  Activity,
  Layers,
  Sparkles
} from 'lucide-react';

export const OverviewDashboard: React.FC = () => {
  const { projects, testSuites, events, runTestSuite, setCurrentView } = useApp();
  const { stats } = useStats();

  const totalTests = stats?.total_tests ?? 2842;
  const passedTests = stats?.passed ?? 2410;
  const failedTests = stats?.failed ?? 84;
  const inProgressTests = stats?.in_progress ?? 348;

  return (
    <div className="space-y-6 pb-12">
      {/* Welcome & Global Actions */}
      <div className="flex flex-col md:flex-row md:items-end justify-between gap-4 pb-2 border-b border-[var(--border-color)]">
        <div>
          <h1 className="text-xl sm:text-2xl font-bold tracking-tight text-[var(--text-primary)]">
            Workspace Overview
          </h1>
          <p className="text-xs sm:text-sm text-[var(--text-secondary)] mt-1">
            Ready for the latest testing cycle. {testSuites.length} suites registered in active pipelines.
          </p>
        </div>
        <div className="flex items-center gap-2.5">
          <button className="btn-outline px-3 py-1.5 text-xs flex items-center gap-1.5">
            <Calendar className="w-3.5 h-3.5 text-[var(--color-okra)]" />
            <span>Last 7 Days</span>
          </button>
          <button 
            onClick={() => alert('Generating PDF & CSV Executive Audit Report...')}
            className="btn-outline px-3 py-1.5 text-xs flex items-center gap-1.5"
          >
            <Download className="w-3.5 h-3.5 text-[var(--color-matcha)]" />
            <span>Export Report</span>
          </button>
        </div>
      </div>

      {/* Top Stat Cards Row */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        {/* Total Tests */}
        <div className="app-card p-4 flex flex-col justify-between h-32 hover:border-[var(--text-secondary)]">
          <div className="flex items-center justify-between">
            <span className="text-xs font-mono font-bold uppercase text-[var(--text-muted)]">
              TOTAL TESTS
            </span>
            <div className="p-2 rounded-md bg-[var(--bg-card-alt)] text-[var(--text-primary)]">
              <Layers className="w-4 h-4 text-[var(--color-okra)]" />
            </div>
          </div>
          <div>
            <p className="text-2xl font-bold text-[var(--text-primary)] font-mono">{totalTests.toLocaleString()}</p>
            <p className="text-xs font-semibold text-[var(--color-matcha)] mt-0.5">+14% vs last cycle</p>
          </div>
        </div>

        {/* Passed Tests */}
        <div className="app-card p-4 flex flex-col justify-between h-32 hover:border-[var(--color-matcha)]">
          <div className="flex items-center justify-between">
            <span className="text-xs font-mono font-bold uppercase text-[var(--text-muted)]">
              PASSED
            </span>
            <div className="p-2 rounded-md badge-matcha">
              <CheckCircle2 className="w-4 h-4" />
            </div>
          </div>
          <div>
            <p className="text-2xl font-bold text-[var(--text-primary)] font-mono">{passedTests.toLocaleString()}</p>
            <div className="w-full bg-[var(--bg-card-alt)] h-1.5 rounded-full mt-2 overflow-hidden">
              <div className="bg-[var(--color-matcha)] h-full rounded-full" style={{ width: '85%' }} />
            </div>
          </div>
        </div>

        {/* Failed Tests */}
        <div className="app-card p-4 flex flex-col justify-between h-32 hover:border-[var(--color-dark-red)]">
          <div className="flex items-center justify-between">
            <span className="text-xs font-mono font-bold uppercase text-[var(--text-muted)]">
              FAILED
            </span>
            <div className="p-2 rounded-md badge-dark-red">
              <AlertCircle className="w-4 h-4" />
            </div>
          </div>
          <div>
            <p className="text-2xl font-bold text-[var(--color-dark-red)] font-mono">{failedTests}</p>
            <p className="text-xs font-semibold text-[var(--color-dark-red)] mt-0.5">Attention required</p>
          </div>
        </div>

        {/* In Progress Tests */}
        <div className="app-card p-4 flex flex-col justify-between h-32 hover:border-[var(--color-orange)]">
          <div className="flex items-center justify-between">
            <span className="text-xs font-mono font-bold uppercase text-[var(--text-muted)]">
              IN PROGRESS
            </span>
            <div className="p-2 rounded-md badge-orange">
              <Activity className="w-4 h-4" />
            </div>
          </div>
          <div>
            <p className="text-2xl font-bold text-[var(--text-primary)] font-mono">{inProgressTests}</p>
            <div className="flex items-center gap-1.5 mt-1">
              <span className="w-2 h-2 rounded-full bg-[var(--color-orange)] animate-ping" />
              <span className="text-xs font-mono text-[var(--color-orange)] font-semibold">Executing live</span>
            </div>
          </div>
        </div>
      </div>

      {/* Main Grid Section (Recent Projects & System Status) */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Recent Projects (Span 2) */}
        <div className="lg:col-span-2 space-y-4">
          <div className="flex items-center justify-between">
            <h2 className="text-base font-bold text-[var(--text-primary)]">Recent Projects</h2>
            <button 
              onClick={() => setCurrentView('projects')} 
              className="text-xs font-mono font-bold text-[var(--color-matcha)] hover:underline"
            >
              View All Projects
            </button>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {projects.map((proj) => (
              <div
                key={proj.id}
                className="app-card p-4 flex flex-col justify-between hover:shadow-md transition-shadow relative overflow-hidden group"
              >
                <div
                  className={`absolute top-0 left-0 right-0 h-1 ${
                    proj.status === 'ACTIVE'
                      ? 'bg-[var(--color-matcha)]'
                      : proj.status === 'CRITICAL'
                      ? 'bg-[var(--color-dark-red)]'
                      : 'bg-[var(--color-orange)]'
                  }`}
                />

                <div className="flex justify-between items-start mb-3 pt-1">
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
                    {proj.status}
                  </span>
                </div>

                <div className="space-y-2 mt-2">
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

                  <div className="flex items-center justify-between pt-3 border-t border-[var(--border-subtle)]">
                    <span className="text-xs text-[var(--text-muted)] font-mono">
                      {proj.openIssues > 0 ? `${proj.openIssues} Critical Issues` : 'All suites green'}
                    </span>
                    <button
                      onClick={() => setCurrentView('boards')}
                      className="text-[var(--text-primary)] hover:text-[var(--color-matcha)] transition-colors flex items-center gap-1 text-xs font-mono"
                    >
                      <span>Board</span>
                      <ArrowRight className="w-3.5 h-3.5" />
                    </button>
                  </div>
                </div>
              </div>
            ))}

            {/* Create New Project Card Button */}
            <div
              onClick={() => setCurrentView('create-project')}
              className="border-2 border-dashed border-[var(--border-color)] hover:border-[var(--color-matcha)] rounded-lg p-5 flex flex-col items-center justify-center text-center cursor-pointer transition-all hover:bg-[var(--bg-card-alt)] group"
            >
              <div className="w-10 h-10 rounded-full bg-[var(--bg-card-alt)] group-hover:bg-[var(--color-matcha-light)] flex items-center justify-center mb-2 transition-colors">
                <Plus className="w-5 h-5 text-[var(--text-muted)] group-hover:text-[var(--color-matcha)]" />
              </div>
              <p className="font-bold text-xs text-[var(--text-primary)] group-hover:text-[var(--color-matcha)]">
                Create New Project
              </p>
              <p className="text-[11px] text-[var(--text-muted)] mt-0.5">
                Initialize test suite & pipeline template
              </p>
            </div>
          </div>
        </div>

        {/* System Status Feed & Weekly Velocity */}
        <div className="space-y-4">
          <h2 className="text-base font-bold text-[var(--text-primary)]">System Status</h2>
          <div className="app-card divide-y divide-[var(--border-color)] overflow-hidden">
            {events.map((evt) => (
              <div key={evt.id} className="p-3.5 flex items-start gap-3">
                <div
                  className={`p-2 rounded-full shrink-0 ${
                    evt.type === 'success'
                      ? 'badge-matcha'
                      : evt.type === 'error'
                      ? 'badge-dark-red'
                      : 'badge-orange'
                  }`}
                >
                  {evt.type === 'success' && <CheckCircle2 className="w-4 h-4" />}
                  {evt.type === 'error' && <AlertCircle className="w-4 h-4" />}
                  {evt.type === 'warning' && <Clock className="w-4 h-4" />}
                  {evt.type === 'info' && <Sparkles className="w-4 h-4" />}
                </div>
                <div className="flex-1">
                  <p className="font-bold text-xs text-[var(--text-primary)]">{evt.title}</p>
                  <p className="text-xs text-[var(--text-secondary)] mt-0.5 leading-snug">
                    {evt.description}
                  </p>
                  <span className="text-[10px] font-mono text-[var(--text-muted)] mt-1 block">
                    {evt.timestamp}
                  </span>
                </div>
              </div>
            ))}
          </div>

          {/* Weekly Velocity Metric Widget */}
          <div className="bg-[var(--text-primary)] text-[var(--bg-main)] rounded-lg p-5 relative overflow-hidden shadow-md">
            <span className="text-[10px] font-mono font-bold tracking-widest uppercase text-[var(--color-matcha)] block">
              WEEKLY VELOCITY
            </span>
            <p className="text-xl font-bold font-mono mt-1">182 Tests/Day</p>
            <p className="text-xs text-[var(--text-muted)] mt-1 flex items-center gap-1">
              <TrendingUp className="w-3.5 h-3.5 text-[var(--color-matcha)]" />
              <span>+12% faster execution cycle than last week</span>
            </p>
          </div>
        </div>
      </div>

      {/* Global Test Stream Table matching Screen 3 */}
      <div className="space-y-3">
        <div className="flex items-center justify-between">
          <h2 className="text-base font-bold text-[var(--text-primary)]">Global Test Stream</h2>
          <div className="flex items-center gap-2">
            <span className="w-2 h-2 rounded-full bg-[var(--color-matcha)] animate-ping" />
            <span className="text-xs font-mono font-bold text-[var(--color-matcha)]">
              LIVE MONITORING
            </span>
          </div>
        </div>

        <div className="overflow-x-auto custom-scrollbar app-card">
          <table className="w-full text-left border-collapse min-w-[700px]">
            <thead>
              <tr className="bg-[var(--bg-card-alt)] text-[10px] font-mono font-bold uppercase text-[var(--text-muted)] border-b border-[var(--border-color)]">
                <th className="px-4 py-3">Suite ID</th>
                <th className="px-4 py-3">Project / Name</th>
                <th className="px-4 py-3">Status</th>
                <th className="px-4 py-3">Duration</th>
                <th className="px-4 py-3">Executor</th>
                <th className="px-4 py-3">Action</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-[var(--border-color)] text-xs font-mono">
              {testSuites.map((suite) => (
                <tr key={suite.id} className="hover:bg-[var(--bg-card-alt)] transition-colors">
                  <td className="px-4 py-3 font-bold text-[var(--text-primary)]">{suite.id}</td>
                  <td className="px-4 py-3 font-sans">
                    <p className="font-bold text-[var(--text-primary)]">{suite.name}</p>
                    <p className="text-[11px] text-[var(--text-muted)] font-mono">{suite.project}</p>
                  </td>
                  <td className="px-4 py-3">
                    <span
                      className={`inline-flex items-center gap-1 px-2 py-0.5 rounded text-[10px] font-bold ${
                        suite.status === 'PASS'
                          ? 'badge-matcha'
                          : suite.status === 'FAIL'
                          ? 'badge-dark-red'
                          : 'badge-orange'
                      }`}
                    >
                      {suite.status}
                    </span>
                  </td>
                  <td className="px-4 py-3 text-[var(--text-secondary)]">{suite.duration}</td>
                  <td className="px-4 py-3 text-[var(--text-muted)]">{suite.executor}</td>
                  <td className="px-4 py-3">
                    <button
                      onClick={() => runTestSuite(suite.id)}
                      disabled={suite.status === 'RUNNING'}
                      className="px-2.5 py-1 text-[11px] btn-outline flex items-center gap-1 hover:border-[var(--color-matcha)] hover:text-[var(--color-matcha)]"
                    >
                      <Play className="w-3 h-3 fill-current" /> Run
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};
