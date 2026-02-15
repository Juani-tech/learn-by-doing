import { Progress } from '@/types';

const STORAGE_KEY = 'learn-by-doing-progress';

export function getProgress(pathId: string): Progress {
  if (typeof window === 'undefined') {
    return {
      pathId,
      completedTasks: [],
      currentTask: null,
      startedAt: new Date().toISOString(),
      lastAccessed: new Date().toISOString()
    };
  }
  
  const stored = localStorage.getItem(STORAGE_KEY);
  if (!stored) {
    const progress: Progress = {
      pathId,
      completedTasks: [],
      currentTask: null,
      startedAt: new Date().toISOString(),
      lastAccessed: new Date().toISOString()
    };
    saveProgress(progress);
    return progress;
  }
  
  const allProgress: Record<string, Progress> = JSON.parse(stored);
  if (!allProgress[pathId]) {
    const progress: Progress = {
      pathId,
      completedTasks: [],
      currentTask: null,
      startedAt: new Date().toISOString(),
      lastAccessed: new Date().toISOString()
    };
    allProgress[pathId] = progress;
    localStorage.setItem(STORAGE_KEY, JSON.stringify(allProgress));
    return progress;
  }
  
  return allProgress[pathId];
}

export function saveProgress(progress: Progress) {
  if (typeof window === 'undefined') return;
  
  const stored = localStorage.getItem(STORAGE_KEY);
  const allProgress: Record<string, Progress> = stored ? JSON.parse(stored) : {};
  
  progress.lastAccessed = new Date().toISOString();
  allProgress[progress.pathId] = progress;
  
  localStorage.setItem(STORAGE_KEY, JSON.stringify(allProgress));
}

export function markTaskComplete(pathId: string, taskId: string) {
  const progress = getProgress(pathId);
  if (!progress.completedTasks.includes(taskId)) {
    progress.completedTasks.push(taskId);
    saveProgress(progress);
  }
}

export function markTaskIncomplete(pathId: string, taskId: string) {
  const progress = getProgress(pathId);
  progress.completedTasks = progress.completedTasks.filter(id => id !== taskId);
  saveProgress(progress);
}

export function setCurrentTask(pathId: string, taskId: string | null) {
  const progress = getProgress(pathId);
  progress.currentTask = taskId;
  saveProgress(progress);
}

export function isTaskComplete(pathId: string, taskId: string): boolean {
  const progress = getProgress(pathId);
  return progress.completedTasks.includes(taskId);
}

export function getCompletionPercentage(pathId: string, totalTasks: number): number {
  const progress = getProgress(pathId);
  if (totalTasks === 0) return 0;
  return Math.round((progress.completedTasks.length / totalTasks) * 100);
}
