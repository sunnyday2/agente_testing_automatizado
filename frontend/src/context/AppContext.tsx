import React, { createContext, useContext, useState } from 'react';
import {
  AppView,
  TaskCard,
  Project,
  TestSuite,
  SystemEvent,
  CategoryTag,
  ViewMode,
  User,
  ColumnType
} from '@/types';
import { initialTasks, initialProjects, initialTestSuites, initialSystemEvents, mockAssignees } from '@/data/mockData';

interface AppContextType {
  currentView: AppView;
  setCurrentView: (view: AppView) => void;
  user: User;
  login: (email: string) => void;
  logout: () => void;
  
  /* Kanban & Task State */
  tasks: TaskCard[];
  selectedBusinessTag: CategoryTag;
  setSelectedBusinessTag: (tag: CategoryTag) => void;
  viewMode: ViewMode;
  setViewMode: (mode: ViewMode) => void;
  searchQuery: string;
  setSearchQuery: (query: string) => void;
  addTask: (task: Omit<TaskCard, 'id'>) => void;
  updateTask: (task: TaskCard) => void;
  moveTaskColumn: (taskId: string, newColumn: ColumnType) => void;
  deleteTask: (taskId: string) => void;

  /* Projects State */
  projects: Project[];
  addProject: (project: Omit<Project, 'id' | 'healthScore' | 'totalSuites' | 'openIssues' | 'lastRun' | 'members'>) => void;

  /* Test Suites State */
  testSuites: TestSuite[];
  runTestSuite: (suiteId: string) => void;

  /* System Events */
  events: SystemEvent[];
}

const defaultUser: User = {
  id: 'usr-0',
  name: '',
  email: '',
  role: '',
  avatar: 'https://images.unsplash.com/photo-1573496359142-b8d87734a5a2?auto=format&fit=crop&w=150&q=80',
  isAuthenticated: false,
};

const AppContext = createContext<AppContextType | undefined>(undefined);

export const AppProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [currentView, setCurrentView] = useState<AppView>('login');
  const [user, setUser] = useState<User>(defaultUser);

  const [tasks, setTasks] = useState<TaskCard[]>(initialTasks);
  const [selectedBusinessTag, setSelectedBusinessTag] = useState<CategoryTag>('ALL');
  const [viewMode, setViewMode] = useState<ViewMode>('Board');
  const [searchQuery, setSearchQuery] = useState<string>('');

  const [projects, setProjects] = useState<Project[]>(initialProjects);
  const [testSuites, setTestSuites] = useState<TestSuite[]>(initialTestSuites);
  const [events, setEvents] = useState<SystemEvent[]>(initialSystemEvents);

  // Check existing session on mount (cookie-based)
  React.useEffect(() => {
    fetch('/api/auth/me', { credentials: 'include' })
      .then(res => {
        if (res.ok) return res.json();
        throw new Error('Not authenticated');
      })
      .then(data => {
        setUser({
          id: data.data.id,
          name: data.data.name,
          email: data.data.email,
          role: data.data.role,
          avatar: 'https://images.unsplash.com/photo-1573496359142-b8d87734a5a2?auto=format&fit=crop&w=150&q=80',
          isAuthenticated: true,
        });
        setCurrentView('overview');
      })
      .catch(() => {
        // No valid session — stay on login
        setUser(prev => ({ ...prev, isAuthenticated: false }));
        setCurrentView('login');
      });
  }, []);

  const login = (email: string) => {
    setUser({
      ...defaultUser,
      email,
      name: email.split('@')[0].toUpperCase(),
      isAuthenticated: true,
      avatar: 'https://images.unsplash.com/photo-1573496359142-b8d87734a5a2?auto=format&fit=crop&w=150&q=80',
    });
    setCurrentView('overview');
  };

  const logout = () => {
    setUser(prev => ({ ...prev, isAuthenticated: false }));
    setCurrentView('login');
  };

  const addTask = (newTaskData: Omit<TaskCard, 'id'>) => {
    const newTask: TaskCard = {
      ...newTaskData,
      id: `TASK-${Math.floor(100 + Math.random() * 900)}`,
      assignees: newTaskData.assignees && newTaskData.assignees.length > 0 ? newTaskData.assignees : [mockAssignees[0]],
    };
    setTasks(prev => [newTask, ...prev]);
  };

  const updateTask = (updatedTask: TaskCard) => {
    setTasks(prev => prev.map(t => (t.id === updatedTask.id ? updatedTask : t)));
  };

  const moveTaskColumn = (taskId: string, newColumn: ColumnType) => {
    setTasks(prev =>
      prev.map(t => (t.id === taskId ? { ...t, column: newColumn } : t))
    );
  };

  const deleteTask = (taskId: string) => {
    setTasks(prev => prev.filter(t => t.id !== taskId));
  };

  const addProject = (projectData: Omit<Project, 'id' | 'healthScore' | 'totalSuites' | 'openIssues' | 'lastRun' | 'members'>) => {
    const newProject: Project = {
      ...projectData,
      id: `prj-${Date.now()}`,
      healthScore: 100,
      totalSuites: 0,
      openIssues: 0,
      lastRun: 'Just created',
      status: 'ACTIVE',
      members: [mockAssignees[0], mockAssignees[1]],
    };
    setProjects(prev => [newProject, ...prev]);
    setEvents(prev => [
      {
        id: `evt-${Date.now()}`,
        title: `Project '${newProject.name}' Created`,
        description: `New ${newProject.environment} workspace initialized with automated pipelines.`,
        timestamp: 'Just now',
        type: 'info',
      },
      ...prev,
    ]);
  };

  const runTestSuite = (suiteId: string) => {
    setTestSuites(prev =>
      prev.map(suite => {
        if (suite.id === suiteId) {
          return {
            ...suite,
            status: 'RUNNING',
            lastRun: 'Running now...',
          };
        }
        return suite;
      })
    );

    // Simulate completion after 2.5 seconds
    setTimeout(() => {
      setTestSuites(prev =>
        prev.map(suite => {
          if (suite.id === suiteId) {
            const isPass = Math.random() > 0.3;
            return {
              ...suite,
              status: isPass ? 'PASS' : 'FAIL',
              lastRun: 'Just now',
              duration: `${(Math.random() * 2 + 1).toFixed(1)}s`,
              passRate: isPass ? 100 : Math.floor(Math.random() * 40 + 50),
            };
          }
          return suite;
        })
      );
    }, 2500);
  };

  return (
    <AppContext.Provider
      value={{
        currentView,
        setCurrentView,
        user,
        login,
        logout,
        tasks,
        selectedBusinessTag,
        setSelectedBusinessTag,
        viewMode,
        setViewMode,
        searchQuery,
        setSearchQuery,
        addTask,
        updateTask,
        moveTaskColumn,
        deleteTask,
        projects,
        addProject,
        testSuites,
        runTestSuite,
        events,
      }}
    >
      {children}
    </AppContext.Provider>
  );
};

export const useApp = () => {
  const context = useContext(AppContext);
  if (!context) {
    throw new Error('useApp must be used within an AppProvider');
  }
  return context;
};
