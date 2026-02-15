export interface LearningPath {
  id: string;
  title: string;
  description: string;
  version: string;
  language: string;
  area: string;
  prerequisites: string[];
  phases: Phase[];
  totalTasks: number;
  estimatedHours: number;
}

export interface Phase {
  id: string;
  title: string;
  description: string;
  order: number;
  tasks: Task[];
}

export interface Task {
  id: string;
  title: string;
  description: string;
  difficulty: 1 | 2 | 3 | 4 | 5;
  estimatedHours: number;
  requirements: string[];
  acceptanceCriteria: string[];
  prerequisites: string[];
  resources: Resource[];
  phaseId: string;
}

export interface Resource {
  title: string;
  url: string;
  type: 'documentation' | 'reference' | 'article' | 'book';
  description: string;
}

export interface Progress {
  pathId: string;
  completedTasks: string[];
  currentTask: string | null;
  startedAt: string;
  lastAccessed: string;
}

export interface PathSummary {
  id: string;
  title: string;
  description: string;
  language: string;
  area: string;
  version: string;
  totalTasks: number;
  estimatedHours: number;
}
