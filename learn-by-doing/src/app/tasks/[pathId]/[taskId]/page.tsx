'use client';

import { useParams } from 'next/navigation';
import { getLearningPath, getTask, getNextTask, getPreviousTask } from '@/lib/paths';
import { getProgress, markTaskComplete, markTaskIncomplete, isTaskComplete, setCurrentTask } from '@/lib/storage';
import Link from 'next/link';
import { CheckCircle2, Circle, Clock, ChevronLeft, ChevronRight, ExternalLink, AlertCircle, CheckSquare } from 'lucide-react';
import { useEffect, useState } from 'react';

export default function TaskPage() {
  const params = useParams();
  const pathId = params.pathId as string;
  const taskId = params.taskId as string;
  
  const path = getLearningPath(pathId);
  const taskData = getTask(pathId, taskId);
  const [completed, setCompleted] = useState(false);
  
  useEffect(() => {
    if (taskId) {
      setCompleted(isTaskComplete(pathId, taskId));
      setCurrentTask(pathId, taskId);
    }
  }, [pathId, taskId]);

  if (!path || !taskData) {
    return (
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-16">
        <div className="text-center">
          <h1 className="text-3xl font-bold text-gray-900 mb-4">Task Not Found</h1>
          <Link href={`/paths/${pathId}`} className="text-[#cc9543] hover:underline">
            Back to Path
          </Link>
        </div>
      </div>
    );
  }

  const { task, phase } = taskData;
  const nextTask = getNextTask(pathId, taskId);
  const prevTask = getPreviousTask(pathId, taskId);
  const progress = getProgress(pathId);

  const handleToggleComplete = () => {
    if (completed) {
      markTaskIncomplete(pathId, taskId);
      setCompleted(false);
    } else {
      markTaskComplete(pathId, taskId);
      setCompleted(true);
    }
  };

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Task Header */}
      <div className="bg-white border-b border-gray-200 sticky top-16 z-40">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-4">
              <Link 
                href={`/paths/${pathId}`}
                className="text-gray-500 hover:text-gray-900 flex items-center gap-1"
              >
                <ChevronLeft className="h-5 w-5" />
                <span className="hidden sm:inline">Back to {path.title}</span>
              </Link>
            </div>

            <div className="flex items-center gap-4">
              {prevTask && (
                <Link
                  href={`/tasks/${pathId}/${prevTask.id}`}
                  className="flex items-center gap-1 text-gray-600 hover:text-gray-900"
                >
                  <ChevronLeft className="h-5 w-5" />
                  <span className="hidden sm:inline">Previous</span>
                </Link>
              )}
              {nextTask && (
                <Link
                  href={`/tasks/${pathId}/${nextTask.id}`}
                  className="flex items-center gap-1 text-gray-600 hover:text-gray-900"
                >
                  <span className="hidden sm:inline">Next</span>
                  <ChevronRight className="h-5 w-5" />
                </Link>
              )}
            </div>
          </div>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="grid lg:grid-cols-3 gap-8">
          {/* Main Content */}
          <div className="lg:col-span-2 space-y-6">
            {/* Title Section */}
            <div className="bg-white rounded-lg border border-gray-200 p-6">
              <div className="flex items-start justify-between gap-4 mb-4">
                <div>
                  <span className="text-sm text-gray-500 mb-2 block">{phase.title}</span>
                  <h1 className="text-3xl font-bold text-gray-900">{task.title}</h1>
                </div>
                <button
                  onClick={handleToggleComplete}
                  className={`flex items-center gap-2 px-4 py-2 rounded-lg font-medium transition-colors ${
                    completed 
                      ? 'bg-green-100 text-green-700 hover:bg-green-200' 
                      : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                  }`}
                >
                  {completed ? (
                    <>
                      <CheckCircle2 className="h-5 w-5" />
                      <span>Completed</span>
                    </>
                  ) : (
                    <>
                      <Circle className="h-5 w-5" />
                      <span>Mark Complete</span>
                    </>
                  )}
                </button>
              </div>

              <p className="text-lg text-gray-700 mb-6">{task.description}</p>

              <div className="flex flex-wrap items-center gap-4 text-sm text-gray-600">
                <div className="flex items-center gap-1">
                  <Clock className="h-4 w-4" />
                  <span>{task.estimatedHours} hours</span>
                </div>
                <div className="flex items-center gap-2">
                  <span>Difficulty:</span>
                  <div className="flex">
                    {Array.from({ length: 5 }).map((_, i) => (
                      <span
                        key={i}
                        className={`w-2.5 h-2.5 rounded-full mx-0.5 ${
                          i < task.difficulty ? 'bg-[#cc9543]' : 'bg-gray-200'
                        }`}
                      />
                    ))}
                  </div>
                </div>
              </div>
            </div>

            {/* Requirements Section */}
            <div className="bg-white rounded-lg border border-gray-200 p-6">
              <h2 className="text-xl font-bold text-gray-900 mb-4 flex items-center gap-2">
                <AlertCircle className="h-5 w-5 text-[#cc9543]" />
                Requirements
              </h2>
              <ul className="space-y-3">
                {task.requirements.map((req, index) => (
                  <li key={index} className="flex items-start gap-3">
                    <span className="flex-shrink-0 w-6 h-6 bg-[#cc9543] text-white rounded-full flex items-center justify-center text-sm font-medium">
                      {index + 1}
                    </span>
                    <span className="text-gray-700 pt-0.5">{req}</span>
                  </li>
                ))}
              </ul>
            </div>

            {/* Acceptance Criteria Section */}
            <div className="bg-white rounded-lg border border-gray-200 p-6">
              <h2 className="text-xl font-bold text-gray-900 mb-4 flex items-center gap-2">
                <CheckSquare className="h-5 w-5 text-green-600" />
                Acceptance Criteria
              </h2>
              <ul className="space-y-3">
                {task.acceptanceCriteria.map((criteria, index) => (
                  <li key={index} className="flex items-start gap-3">
                    <span className="flex-shrink-0 w-6 h-6 bg-green-100 text-green-700 rounded-full flex items-center justify-center">
                      <CheckCircle2 className="h-4 w-4" />
                    </span>
                    <span className="text-gray-700 pt-0.5">{criteria}</span>
                  </li>
                ))}
              </ul>
            </div>
          </div>

          {/* Sidebar */}
          <div className="space-y-6">
            {/* Resources Section */}
            <div className="bg-white rounded-lg border border-gray-200 p-6">
              <h2 className="text-lg font-bold text-gray-900 mb-4">Resources</h2>
              <p className="text-sm text-gray-600 mb-4">
                Use these official references and documentation. We intentionally filter out 
                tutorials and solutions.
              </p>
              <div className="space-y-3">
                {task.resources.map((resource, index) => (
                  <a
                    key={index}
                    href={resource.url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="block p-3 bg-gray-50 rounded-lg hover:bg-orange-50 transition-colors group"
                  >
                    <div className="flex items-start justify-between gap-2">
                      <div className="flex-1 min-w-0">
                        <h3 className="font-medium text-gray-900 group-hover:text-[#cc9543] transition-colors line-clamp-1">
                          {resource.title}
                        </h3>
                        <p className="text-sm text-gray-600 mt-1">{resource.description}</p>
                        <span className="inline-block mt-2 text-xs px-2 py-0.5 bg-gray-200 text-gray-700 rounded">
                          {resource.type}
                        </span>
                      </div>
                      <ExternalLink className="h-4 w-4 text-gray-400 flex-shrink-0" />
                    </div>
                  </a>
                ))}
              </div>
            </div>

            {/* Prerequisites Section */}
            {task.prerequisites.length > 0 && (
              <div className="bg-white rounded-lg border border-gray-200 p-6">
                <h2 className="text-lg font-bold text-gray-900 mb-4">Prerequisites</h2>
                <ul className="space-y-2">
                  {task.prerequisites.map((prereqId) => {
                    const prereqTask = getTask(pathId, prereqId);
                    const isPrereqComplete = progress.completedTasks.includes(prereqId);
                    
                    if (!prereqTask) return null;
                    
                    return (
                      <li key={prereqId}>
                        <Link
                          href={`/tasks/${pathId}/${prereqId}`}
                          className="flex items-center gap-2 text-gray-600 hover:text-[#cc9543]"
                        >
                          {isPrereqComplete ? (
                            <CheckCircle2 className="h-4 w-4 text-green-500" />
                          ) : (
                            <Circle className="h-4 w-4" />
                          )}
                          <span className={isPrereqComplete ? 'line-through text-gray-400' : ''}>
                            {prereqTask.task.title}
                          </span>
                        </Link>
                      </li>
                    );
                  })}
                </ul>
              </div>
            )}

            {/* Progress Overview */}
            <div className="bg-white rounded-lg border border-gray-200 p-6">
              <h2 className="text-lg font-bold text-gray-900 mb-4">Your Progress</h2>
              <div className="space-y-3">
                <div className="flex justify-between text-sm">
                  <span className="text-gray-600">Completed</span>
                  <span className="font-medium">{progress.completedTasks.length} / {path.totalTasks}</span>
                </div>
                <div className="w-full bg-gray-200 rounded-full h-2">
                  <div 
                    className="bg-[#cc9543] h-2 rounded-full transition-all"
                    style={{ width: `${(progress.completedTasks.length / path.totalTasks) * 100}%` }}
                  />
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
