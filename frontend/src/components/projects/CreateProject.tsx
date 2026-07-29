import React, { useState } from 'react';
import { useApp } from '@/context/AppContext';
import { 
  ChevronRight, 
  Rocket, 
  FlaskConical, 
  Terminal, 
  CheckCircle2, 
  ArrowLeft,
  Server,
  MessageSquare,
  FileCode,
  Database
} from 'lucide-react';

export const CreateProject: React.FC = () => {
  const { addProject, setCurrentView } = useApp();

  const [name, setName] = useState('');
  const [subtitle, setSubtitle] = useState('');
  const [environment, setEnvironment] = useState<'Production' | 'Staging' | 'Dev'>('Production');
  const [visibility, setVisibility] = useState<'Public' | 'Private'>('Public');

  const [jenkins, setJenkins] = useState(false);
  const [slack, setSlack] = useState(true);
  const [jira, setJira] = useState(false);
  const [s3, setS3] = useState(false);

  const [isSuccessModalOpen, setIsSuccessModalOpen] = useState(false);
  const [progressWidth, setProgressWidth] = useState(0);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!name.trim()) return;

    addProject({
      name,
      subtitle: subtitle || 'Custom Automation Suite',
      environment,
      visibility,
      status: 'ACTIVE',
      integrations: { jenkins, slack, jira, s3 },
    });

    setIsSuccessModalOpen(true);
    let current = 0;
    const interval = setInterval(() => {
      current += 10;
      setProgressWidth(current);
      if (current >= 100) {
        clearInterval(interval);
        setTimeout(() => {
          setIsSuccessModalOpen(false);
          setCurrentView('boards');
        }, 600);
      }
    }, 80);
  };

  return (
    <div className="max-w-4xl mx-auto space-y-6 pb-16">
      {/* Breadcrumb Context */}
      <div className="flex items-center gap-1.5 text-xs font-mono text-[var(--text-muted)]">
        <button onClick={() => setCurrentView('projects')} className="hover:text-[var(--text-primary)]">
          Projects
        </button>
        <ChevronRight className="w-3.5 h-3.5" />
        <span className="text-[var(--text-primary)] font-bold">New Project</span>
      </div>

      {/* Page Header */}
      <div>
        <h1 className="text-xl sm:text-2xl font-bold tracking-tight text-[var(--text-primary)]">
          Create New Project
        </h1>
        <p className="text-xs sm:text-sm text-[var(--text-secondary)] mt-1">
          Configure a new automation workspace to begin orchestrating your testing suites and CI/CD pipelines.
        </p>
      </div>

      <form onSubmit={handleSubmit} className="space-y-6">
        {/* Step 1: Project Details */}
        <section className="app-card overflow-hidden">
          <div className="p-4 border-b border-[var(--border-color)] bg-[var(--bg-card-alt)] flex items-center justify-between">
            <div className="flex items-center gap-2.5">
              <div className="p-1.5 rounded bg-[var(--text-primary)] text-[var(--bg-card)]">
                <Rocket className="w-4 h-4 text-[var(--color-matcha)]" />
              </div>
              <h2 className="font-bold text-sm">Project Details</h2>
            </div>
            <span className="text-[10px] font-mono font-bold uppercase text-[var(--text-muted)] tracking-wider">
              STEP 1 OF 3
            </span>
          </div>

          <div className="p-6 space-y-5">
            <div>
              <label className="block text-xs font-mono font-bold uppercase mb-1">
                Project Name <span className="text-[var(--color-dark-red)]">*</span>
              </label>
              <input
                type="text"
                required
                value={name}
                onChange={(e) => setName(e.target.value)}
                placeholder="e.g. Core Checkout API"
                className="w-full px-4 py-2.5 bg-[var(--bg-card-alt)] border border-[var(--border-color)] rounded text-sm text-[var(--text-primary)] focus:outline-none focus:ring-1 focus:ring-[var(--color-matcha)]"
              />
              <p className="text-[11px] text-[var(--text-muted)] mt-1 font-mono">
                This will be used as the primary identifier across reports and dashboards.
              </p>
            </div>

            <div>
              <label className="block text-xs font-mono font-bold uppercase mb-1">
                Description / Subtitle
              </label>
              <textarea
                rows={3}
                value={subtitle}
                onChange={(e) => setSubtitle(e.target.value)}
                placeholder="Briefly describe the scope of this project..."
                className="w-full px-4 py-2.5 bg-[var(--bg-card-alt)] border border-[var(--border-color)] rounded text-sm text-[var(--text-primary)] focus:outline-none focus:ring-1 focus:ring-[var(--color-matcha)]"
              />
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-6 pt-2">
              <div>
                <label className="block text-xs font-mono font-bold uppercase mb-2">
                  Target Environment
                </label>
                <div className="grid grid-cols-3 gap-2">
                  <button
                    type="button"
                    onClick={() => setEnvironment('Production')}
                    className={`py-2 px-3 border rounded text-xs font-mono flex flex-col items-center gap-1 transition-all ${
                      environment === 'Production'
                        ? 'bg-[var(--text-primary)] text-[var(--bg-card)] border-[var(--text-primary)] font-bold'
                        : 'bg-[var(--bg-card-alt)] text-[var(--text-secondary)] border-[var(--border-color)] hover:border-[var(--text-secondary)]'
                    }`}
                  >
                    <Rocket className="w-4 h-4 text-[var(--color-matcha)]" />
                    <span>Production</span>
                  </button>

                  <button
                    type="button"
                    onClick={() => setEnvironment('Staging')}
                    className={`py-2 px-3 border rounded text-xs font-mono flex flex-col items-center gap-1 transition-all ${
                      environment === 'Staging'
                        ? 'bg-[var(--text-primary)] text-[var(--bg-card)] border-[var(--text-primary)] font-bold'
                        : 'bg-[var(--bg-card-alt)] text-[var(--text-secondary)] border-[var(--border-color)] hover:border-[var(--text-secondary)]'
                    }`}
                  >
                    <FlaskConical className="w-4 h-4 text-[var(--color-orange)]" />
                    <span>Staging</span>
                  </button>

                  <button
                    type="button"
                    onClick={() => setEnvironment('Dev')}
                    className={`py-2 px-3 border rounded text-xs font-mono flex flex-col items-center gap-1 transition-all ${
                      environment === 'Dev'
                        ? 'bg-[var(--text-primary)] text-[var(--bg-card)] border-[var(--text-primary)] font-bold'
                        : 'bg-[var(--bg-card-alt)] text-[var(--text-secondary)] border-[var(--border-color)] hover:border-[var(--text-secondary)]'
                    }`}
                  >
                    <Terminal className="w-4 h-4 text-[var(--color-okra)]" />
                    <span>Dev</span>
                  </button>
                </div>
              </div>

              <div>
                <label className="block text-xs font-mono font-bold uppercase mb-2">
                  Visibility
                </label>
                <div className="flex items-center gap-6 py-2">
                  <label className="flex items-center gap-2 text-xs font-medium cursor-pointer">
                    <input
                      type="radio"
                      name="visibility"
                      checked={visibility === 'Public'}
                      onChange={() => setVisibility('Public')}
                      className="accent-[var(--color-matcha)]"
                    />
                    <span>Public (Team Access)</span>
                  </label>
                  <label className="flex items-center gap-2 text-xs font-medium cursor-pointer">
                    <input
                      type="radio"
                      name="visibility"
                      checked={visibility === 'Private'}
                      onChange={() => setVisibility('Private')}
                      className="accent-[var(--color-matcha)]"
                    />
                    <span>Private (Restricted)</span>
                  </label>
                </div>
              </div>
            </div>
          </div>
        </section>

        {/* Step 2: Integration Settings */}
        <section className="app-card overflow-hidden">
          <div className="p-4 border-b border-[var(--border-color)] bg-[var(--bg-card-alt)] flex items-center justify-between">
            <div className="flex items-center gap-2.5">
              <div className="p-1.5 rounded badge-matcha">
                <Server className="w-4 h-4" />
              </div>
              <h2 className="font-bold text-sm">Integration Settings</h2>
            </div>
            <span className="text-[10px] font-mono font-bold uppercase text-[var(--text-muted)] tracking-wider">
              STEP 2 OF 3
            </span>
          </div>

          <div className="p-6">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {/* Jenkins */}
              <div
                onClick={() => setJenkins(!jenkins)}
                className={`p-4 border rounded-lg flex items-center justify-between cursor-pointer transition-colors ${
                  jenkins
                    ? 'border-[var(--color-matcha)] bg-[var(--color-matcha-light)]'
                    : 'border-[var(--border-color)] bg-[var(--bg-card-alt)] hover:border-[var(--text-secondary)]'
                }`}
              >
                <div className="flex items-center gap-3">
                  <div className="p-2 rounded bg-[var(--bg-card)] border border-[var(--border-color)]">
                    <Server className="w-4 h-4 text-[var(--text-primary)]" />
                  </div>
                  <div>
                    <p className="font-bold text-xs text-[var(--text-primary)]">Jenkins CI</p>
                    <p className="text-[11px] text-[var(--text-muted)]">Automated webhooks & triggers</p>
                  </div>
                </div>
                <div className={`w-9 h-5 rounded-full p-0.5 transition-colors ${jenkins ? 'bg-[var(--color-matcha)]' : 'bg-[var(--border-color)]'}`}>
                  <div className={`w-4 h-4 rounded-full bg-[var(--bg-card)] transition-transform ${jenkins ? 'translate-x-4' : ''}`} />
                </div>
              </div>

              {/* Slack */}
              <div
                onClick={() => setSlack(!slack)}
                className={`p-4 border rounded-lg flex items-center justify-between cursor-pointer transition-colors ${
                  slack
                    ? 'border-[var(--color-matcha)] bg-[var(--color-matcha-light)]'
                    : 'border-[var(--border-color)] bg-[var(--bg-card-alt)] hover:border-[var(--text-secondary)]'
                }`}
              >
                <div className="flex items-center gap-3">
                  <div className="p-2 rounded bg-[var(--bg-card)] border border-[var(--border-color)]">
                    <MessageSquare className="w-4 h-4 text-[var(--text-primary)]" />
                  </div>
                  <div>
                    <p className="font-bold text-xs text-[var(--text-primary)]">Slack Alerts</p>
                    <p className="text-[11px] text-[var(--text-muted)]">Real-time status notifications</p>
                  </div>
                </div>
                <div className={`w-9 h-5 rounded-full p-0.5 transition-colors ${slack ? 'bg-[var(--color-matcha)]' : 'bg-[var(--border-color)]'}`}>
                  <div className={`w-4 h-4 rounded-full bg-[var(--bg-card)] transition-transform ${slack ? 'translate-x-4' : ''}`} />
                </div>
              </div>

              {/* Jira */}
              <div
                onClick={() => setJira(!jira)}
                className={`p-4 border rounded-lg flex items-center justify-between cursor-pointer transition-colors ${
                  jira
                    ? 'border-[var(--color-matcha)] bg-[var(--color-matcha-light)]'
                    : 'border-[var(--border-color)] bg-[var(--bg-card-alt)] hover:border-[var(--text-secondary)]'
                }`}
              >
                <div className="flex items-center gap-3">
                  <div className="p-2 rounded bg-[var(--bg-card)] border border-[var(--border-color)]">
                    <FileCode className="w-4 h-4 text-[var(--text-primary)]" />
                  </div>
                  <div>
                    <p className="font-bold text-xs text-[var(--text-primary)]">Jira Software</p>
                    <p className="text-[11px] text-[var(--text-muted)]">Automatic bug ticket syncing</p>
                  </div>
                </div>
                <div className={`w-9 h-5 rounded-full p-0.5 transition-colors ${jira ? 'bg-[var(--color-matcha)]' : 'bg-[var(--border-color)]'}`}>
                  <div className={`w-4 h-4 rounded-full bg-[var(--bg-card)] transition-transform ${jira ? 'translate-x-4' : ''}`} />
                </div>
              </div>

              {/* S3 Bucket */}
              <div
                onClick={() => setS3(!s3)}
                className={`p-4 border rounded-lg flex items-center justify-between cursor-pointer transition-colors ${
                  s3
                    ? 'border-[var(--color-matcha)] bg-[var(--color-matcha-light)]'
                    : 'border-[var(--border-color)] bg-[var(--bg-card-alt)] hover:border-[var(--text-secondary)]'
                }`}
              >
                <div className="flex items-center gap-3">
                  <div className="p-2 rounded bg-[var(--bg-card)] border border-[var(--border-color)]">
                    <Database className="w-4 h-4 text-[var(--text-primary)]" />
                  </div>
                  <div>
                    <p className="font-bold text-xs text-[var(--text-primary)]">S3 Bucket</p>
                    <p className="text-[11px] text-[var(--text-muted)]">Test logs & artifact storage</p>
                  </div>
                </div>
                <div className={`w-9 h-5 rounded-full p-0.5 transition-colors ${s3 ? 'bg-[var(--color-matcha)]' : 'bg-[var(--border-color)]'}`}>
                  <div className={`w-4 h-4 rounded-full bg-[var(--bg-card)] transition-transform ${s3 ? 'translate-x-4' : ''}`} />
                </div>
              </div>
            </div>
          </div>
        </section>

        {/* Action Footer */}
        <div className="flex items-center justify-between pt-4">
          <button
            type="button"
            onClick={() => setCurrentView('projects')}
            className="btn-outline px-4 py-2 text-xs flex items-center gap-1.5"
          >
            <ArrowLeft className="w-4 h-4" /> Back to Projects
          </button>

          <div className="flex items-center gap-3">
            <button
              type="button"
              onClick={() => alert('Draft saved successfully!')}
              className="px-4 py-2 text-xs font-mono text-[var(--text-muted)] hover:text-[var(--text-primary)] font-semibold"
            >
              Save Draft
            </button>
            <button
              type="submit"
              className="btn-matcha px-6 py-2.5 text-xs font-mono font-bold flex items-center gap-2 shadow-md"
            >
              <span>Create Project</span>
              <Rocket className="w-4 h-4" />
            </button>
          </div>
        </div>
      </form>

      {/* Success Modal Overlay */}
      {isSuccessModalOpen && (
        <div className="fixed inset-0 z-50 bg-black/70 backdrop-blur-xs flex items-center justify-center p-4">
          <div className="app-card w-full max-w-sm p-6 text-center space-y-4 shadow-2xl bg-[var(--bg-card)] border border-[var(--border-color)]">
            <div className="w-14 h-14 rounded-full badge-matcha flex items-center justify-center mx-auto">
              <CheckCircle2 className="w-8 h-8" />
            </div>
            <h3 className="text-lg font-bold text-[var(--text-primary)]">Project Workspace Created!</h3>
            <p className="text-xs text-[var(--text-secondary)]">
              Redirecting you to active boards...
            </p>
            <div className="w-full bg-[var(--bg-card-alt)] h-1.5 rounded-full overflow-hidden">
              <div
                className="bg-[var(--color-matcha)] h-full transition-all duration-100"
                style={{ width: `${progressWidth}%` }}
              />
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
