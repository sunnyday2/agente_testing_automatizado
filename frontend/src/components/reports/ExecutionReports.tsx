import React from 'react';
import { useApp } from '@/context/AppContext';
import { useReports } from '@/hooks/useReports';
import { 
  BarChart, 
  Bar, 
  XAxis, 
  YAxis, 
  CartesianGrid, 
  Tooltip, 
  ResponsiveContainer, 
  PieChart, 
  Pie, 
  Cell, 
  AreaChart, 
  Area 
} from 'recharts';
import { TrendingUp, AlertTriangle, CheckCircle2, Download } from 'lucide-react';

export const ExecutionReports: React.FC = () => {
  const { testSuites } = useApp();
  const { analytics, exportCsv } = useReports();

  const velocityData = analytics?.velocity ?? [
    { day: 'Mon', passed: 320, failed: 12, inProgress: 45 },
    { day: 'Tue', passed: 410, failed: 18, inProgress: 30 },
    { day: 'Wed', passed: 390, failed: 8, inProgress: 52 },
    { day: 'Thu', passed: 510, failed: 24, inProgress: 60 },
    { day: 'Fri', passed: 480, failed: 14, inProgress: 40 },
    { day: 'Sat', passed: 210, failed: 4, inProgress: 15 },
    { day: 'Sun', passed: 180, failed: 2, inProgress: 10 },
  ];

  const failureCategoryData = analytics?.failures ?? [
    { name: '500 Server Error', value: 38, color: 'var(--color-dark-red)' },
    { name: 'Timeout / Latency', value: 24, color: 'var(--color-orange)' },
    { name: 'Assertion Mismatch', value: 18, color: 'var(--color-okra)' },
    { name: 'Auth/HMAC Signature', value: 12, color: 'var(--color-brown)' },
  ];

  const passRateByEnv = analytics?.pass_rate_by_env ?? [
    { env: 'Production', rate: 98.4 },
    { env: 'Staging', rate: 91.2 },
    { env: 'Dev Sandbox', rate: 84.6 },
  ];

  return (
    <div className="space-y-6 pb-12">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-2 border-b border-[var(--border-color)]">
        <div>
          <h1 className="text-xl sm:text-2xl font-bold tracking-tight text-[var(--text-primary)]">
            Execution Analytics & Reports
          </h1>
          <p className="text-xs sm:text-sm text-[var(--text-secondary)] mt-1">
            Quality metrics, regression velocity, pass rate breakdowns, and failure category taxonomy.
          </p>
        </div>
        <div className="flex items-center gap-2">
          <button 
            onClick={() => exportCsv()}
            className="btn-outline px-3 py-1.5 text-xs flex items-center gap-1.5"
          >
            <Download className="w-3.5 h-3.5 text-[var(--color-matcha)]" />
            <span>Download CSV</span>
          </button>
        </div>
      </div>

      {/* Top Stat Row */}
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
        <div className="app-card p-4">
          <div className="flex items-center justify-between">
            <span className="text-xs font-mono font-bold text-[var(--text-muted)] uppercase">Overall Pass Rate</span>
            <CheckCircle2 className="w-4 h-4 text-[var(--color-matcha)]" />
          </div>
          <p className="text-2xl font-bold font-mono text-[var(--text-primary)] mt-2">94.8%</p>
          <span className="text-xs text-[var(--color-matcha)] font-semibold mt-1 block">+1.2% this week</span>
        </div>

        <div className="app-card p-4">
          <div className="flex items-center justify-between">
            <span className="text-xs font-mono font-bold text-[var(--text-muted)] uppercase">Mean Time To Detect (MTTD)</span>
            <TrendingUp className="w-4 h-4 text-[var(--color-orange)]" />
          </div>
          <p className="text-2xl font-bold font-mono text-[var(--text-primary)] mt-2">4.2 min</p>
          <span className="text-xs text-[var(--color-matcha)] font-semibold mt-1 block">-1.8 min faster</span>
        </div>

        <div className="app-card p-4">
          <div className="flex items-center justify-between">
            <span className="text-xs font-mono font-bold text-[var(--text-muted)] uppercase">Active Regressions</span>
            <AlertTriangle className="w-4 h-4 text-[var(--color-dark-red)]" />
          </div>
          <p className="text-2xl font-bold font-mono text-[var(--color-dark-red)] mt-2">3 Bugs</p>
          <span className="text-xs text-[var(--text-muted)] font-mono mt-1 block">2 High, 1 Medium</span>
        </div>
      </div>

      {/* Charts Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Weekly Execution Velocity Area Chart */}
        <div className="app-card p-4 space-y-3">
          <div className="flex items-center justify-between pb-2 border-b border-[var(--border-color)]">
            <h3 className="font-bold text-xs sm:text-sm font-mono uppercase text-[var(--text-primary)]">
              Daily Test Execution Volume
            </h3>
            <span className="text-[10px] font-mono badge-matcha px-2 py-0.5 rounded">PASSED VS FAILED</span>
          </div>

          <div className="h-64 w-full pt-2">
            <ResponsiveContainer width="100%" height="100%">
              <AreaChart data={velocityData}>
                <CartesianGrid strokeDasharray="3 3" stroke="var(--border-color)" />
                <XAxis dataKey="day" stroke="var(--text-muted)" fontSize={11} tickLine={false} />
                <YAxis stroke="var(--text-muted)" fontSize={11} tickLine={false} />
                <Tooltip
                  contentStyle={{
                    backgroundColor: 'var(--bg-card)',
                    borderColor: 'var(--border-color)',
                    borderRadius: '6px',
                    fontSize: '12px',
                    color: 'var(--text-primary)',
                  }}
                />
                <Area type="monotone" dataKey="passed" stackId="1" stroke="var(--color-matcha)" fill="var(--color-matcha-light)" />
                <Area type="monotone" dataKey="failed" stackId="1" stroke="var(--color-dark-red)" fill="var(--color-dark-red-light)" />
              </AreaChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Failure Category Taxonomy Pie Chart */}
        <div className="app-card p-4 space-y-3">
          <div className="flex items-center justify-between pb-2 border-b border-[var(--border-color)]">
            <h3 className="font-bold text-xs sm:text-sm font-mono uppercase text-[var(--text-primary)]">
              Failure Root Causes Breakdown
            </h3>
            <span className="text-[10px] font-mono badge-dark-red px-2 py-0.5 rounded">TAXONOMY</span>
          </div>

          <div className="h-64 w-full flex items-center justify-center pt-2">
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie
                  data={failureCategoryData}
                  cx="50%"
                  cy="50%"
                  innerRadius={55}
                  outerRadius={85}
                  paddingAngle={4}
                  dataKey="value"
                >
                  {failureCategoryData.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={entry.color} />
                  ))}
                </Pie>
                <Tooltip
                  contentStyle={{
                    backgroundColor: 'var(--bg-card)',
                    borderColor: 'var(--border-color)',
                    borderRadius: '6px',
                    fontSize: '12px',
                    color: 'var(--text-primary)',
                  }}
                />
              </PieChart>
            </ResponsiveContainer>
          </div>

          {/* Legend */}
          <div className="grid grid-cols-2 gap-2 pt-2 text-xs font-mono">
            {failureCategoryData.map((item) => (
              <div key={item.name} className="flex items-center gap-2">
                <span className="w-2.5 h-2.5 rounded-full" style={{ backgroundColor: item.color }} />
                <span className="text-[var(--text-secondary)] truncate">{item.name} ({item.value}%)</span>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Environment Pass Rate Bar Chart */}
      <div className="app-card p-4 space-y-3">
        <div className="flex items-center justify-between pb-2 border-b border-[var(--border-color)]">
          <h3 className="font-bold text-xs sm:text-sm font-mono uppercase text-[var(--text-primary)]">
            Pass Rate Stability by Environment
          </h3>
        </div>

        <div className="h-48 w-full pt-2">
          <ResponsiveContainer width="100%" height="100%">
            <BarChart data={passRateByEnv} layout="vertical">
              <CartesianGrid strokeDasharray="3 3" stroke="var(--border-color)" />
              <XAxis type="number" domain={[0, 100]} stroke="var(--text-muted)" fontSize={11} />
              <YAxis dataKey="env" type="category" stroke="var(--text-muted)" fontSize={11} tickLine={false} width={100} />
              <Tooltip
                contentStyle={{
                  backgroundColor: 'var(--bg-card)',
                  borderColor: 'var(--border-color)',
                  borderRadius: '6px',
                  fontSize: '12px',
                }}
              />
              <Bar dataKey="rate" fill="var(--color-matcha)" radius={[0, 4, 4, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>
    </div>
  );
};
