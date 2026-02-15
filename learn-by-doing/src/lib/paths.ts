import { LearningPath } from '@/types';
import pathData from '@/data/paths/cpp-systems-cpp20.json';

export function getLearningPath(id: string): LearningPath | null {
  if (id === 'cpp-systems-cpp20') {
    return pathData as LearningPath;
  }
  return null;
}

export function getAllLearningPaths(): LearningPath[] {
  return [pathData as LearningPath];
}

export function getTask(pathId: string, taskId: string) {
  const path = getLearningPath(pathId);
  if (!path) return null;
  
  for (const phase of path.phases) {
    const task = phase.tasks.find(t => t.id === taskId);
    if (task) return { task, phase, path };
  }
  return null;
}

export function getNextTask(pathId: string, currentTaskId: string) {
  const path = getLearningPath(pathId);
  if (!path) return null;
  
  let found = false;
  for (const phase of path.phases) {
    for (const task of phase.tasks) {
      if (found) return task;
      if (task.id === currentTaskId) found = true;
    }
  }
  return null;
}

export function getPreviousTask(pathId: string, currentTaskId: string) {
  const path = getLearningPath(pathId);
  if (!path) return null;
  
  let prevTask = null;
  for (const phase of path.phases) {
    for (const task of phase.tasks) {
      if (task.id === currentTaskId) return prevTask;
      prevTask = task;
    }
  }
  return null;
}
