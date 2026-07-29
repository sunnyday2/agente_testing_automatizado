import { useState } from 'react';
import { BookOpen, Database, RefreshCw } from 'lucide-react';
import { useStories } from '@/hooks/useStories';
import { StoryCard } from '@/components/stories/StoryCard';
import { StoryUploadForm } from '@/components/stories/StoryUploadForm';
import { StoryDetailModal } from '@/components/stories/StoryDetailModal';
import { LoadingSkeleton } from '@/components/shared/LoadingSkeleton';
import { EmptyState } from '@/components/shared/EmptyState';
import type { Story } from '@/services/storiesService';

export function StoriesPage() {
  const {
    stories,
    isLoading,
    error,
    createStory,
    deleteStory,
    seedStories,
    isSeedingInProgress,
  } = useStories();

  const [viewingStory, setViewingStory] = useState<Story | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);

  const indexedCount = stories.filter(s => s.is_indexed).length;
  const totalScenarios = stories.reduce((acc, s) => acc + s.test_scenarios_count, 0);

  const handleCreate = async (data: Parameters<typeof createStory>[0]) => {
    setIsSubmitting(true);
    try {
      await createStory(data);
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleSeed = async () => {
    try {
      const count = await seedStories();
      alert(`Successfully indexed ${count} stories into ChromaDB`);
    } catch {
      // Error is shown via the hook's error state
    }
  };

  return (
    <div className="space-y-6 pb-12">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-2 border-b border-[var(--border-color)]">
        <div>
          <h1 className="text-xl sm:text-2xl font-bold tracking-tight text-[var(--text-primary)]">
            User Stories
          </h1>
          <p className="text-xs sm:text-sm text-[var(--text-secondary)] mt-1">
            Manage user stories for RAG-powered test generation. Upload, index, and track scenario coverage.
          </p>
        </div>
        <button
          onClick={handleSeed}
          disabled={isSeedingInProgress}
          className="btn-matcha px-4 py-2 text-xs font-mono font-bold flex items-center gap-2 shadow-sm shrink-0 disabled:opacity-50"
        >
          {isSeedingInProgress ? (
            <RefreshCw className="w-4 h-4 animate-spin" />
          ) : (
            <Database className="w-4 h-4" />
          )}
          <span>{isSeedingInProgress ? 'Indexing...' : 'Seed All to ChromaDB'}</span>
        </button>
      </div>

      {/* Stats bar */}
      <div className="flex items-center gap-4 text-xs font-mono bg-[var(--bg-card)] p-3 border border-[var(--border-color)] rounded-lg">
        <span className="font-bold text-[var(--text-primary)]">
          Total <span className="px-1.5 py-0.5 rounded bg-[var(--bg-card-alt)]">{stories.length}</span>
        </span>
        <span className="text-[var(--text-secondary)]">
          Indexed <span className="font-bold text-[var(--color-matcha)]">{indexedCount}</span>
        </span>
        <span className="text-[var(--text-secondary)]">
          Scenarios <span className="font-bold text-[var(--color-okra)]">{totalScenarios}</span>
        </span>
      </div>

      {error && (
        <div className="p-3 bg-[var(--color-dark-red-light)] border border-[var(--color-dark-red)] rounded text-xs text-[var(--color-dark-red)] font-mono" role="alert">
          {error}
        </div>
      )}

      {/* Main layout: form + story grid */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Upload form */}
        <div className="lg:col-span-1">
          <StoryUploadForm onSubmit={handleCreate} isSubmitting={isSubmitting} />
        </div>

        {/* Story grid */}
        <div className="lg:col-span-2 space-y-4">
          <h2 className="text-sm font-bold text-[var(--text-primary)] font-mono uppercase">
            Stored Stories ({stories.length})
          </h2>

          {isLoading ? (
            <LoadingSkeleton lines={5} />
          ) : stories.length === 0 ? (
            <EmptyState
              icon={<BookOpen className="w-6 h-6 text-[var(--text-muted)]" />}
              title="No stories yet"
              description="Upload your first user story to start generating test scenarios with the RAG pipeline."
            />
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
              {stories.map(story => (
                <StoryCard
                  key={story.id}
                  story={story}
                  onView={setViewingStory}
                  onDelete={deleteStory}
                />
              ))}
            </div>
          )}
        </div>
      </div>

      {/* Detail modal */}
      <StoryDetailModal
        story={viewingStory}
        isOpen={viewingStory !== null}
        onClose={() => setViewingStory(null)}
      />
    </div>
  );
}
