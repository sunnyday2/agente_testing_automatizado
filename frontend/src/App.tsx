import { ThemeProvider } from '@/context/ThemeContext';
import { AppProvider, useApp } from '@/context/AppContext';
import { Header } from '@/components/layout/Header';
import { Sidebar } from '@/components/layout/Sidebar';
import { KanbanBoard } from '@/components/kanban/KanbanBoard';
import { OverviewDashboard } from '@/components/dashboard/OverviewDashboard';
import { CreateProject } from '@/components/projects/CreateProject';
import { LoginScreen } from '@/components/auth/LoginScreen';
import { TestSuites } from '@/components/tests/TestSuites';
import { ExecutionReports } from '@/components/reports/ExecutionReports';
import { AllProjects } from '@/components/projects/AllProjects';
import { SettingsPage } from '@/components/settings/SettingsPage';

function AppContent() {
  const { currentView, user } = useApp();

  if (currentView === 'login' || !user.isAuthenticated) {
    return <LoginScreen />;
  }

  return (
    <div className="min-h-screen bg-[var(--bg-main)] text-[var(--text-primary)] font-sans antialiased">
      <Header />
      <div className="flex pt-16 min-h-[calc(100vh-64px)]">
        <Sidebar />
        <main className="flex-1 md:ml-64 p-4 sm:p-6 max-w-7xl mx-auto w-full overflow-x-hidden">
          {currentView === 'overview' && <OverviewDashboard />}
          {currentView === 'boards' && <KanbanBoard />}
          {currentView === 'projects' && <AllProjects />}
          {currentView === 'create-project' && <CreateProject />}
          {currentView === 'tests' && <TestSuites />}
          {currentView === 'reports' && <ExecutionReports />}
          {currentView === 'settings' && <SettingsPage />}
        </main>
      </div>
    </div>
  );
}

export default function App() {
  return (
    <ThemeProvider>
      <AppProvider>
        <AppContent />
      </AppProvider>
    </ThemeProvider>
  );
}
