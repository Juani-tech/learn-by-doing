'use client';

import { useParams } from 'next/navigation';
import { getLearningPath } from '@/lib/paths';
import { getProgress, getCompletionPercentage } from '@/lib/storage';
import Link from 'next/link';
import { CheckCircle2, Circle, Clock, ArrowRight, ChevronLeft } from 'lucide-react';

export default function PathPage() {
  const params = useParams();
  const pathId = params.id as string;
  const path = getLearningPath(pathId);
  const progress = getProgress(pathId);
  const completionPercentage = getCompletionPercentage(pathId, path?.totalTasks || 0);

  if (!path) {
    return (
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-16">
        <div className="text-center">
          <h1 className="text-3xl font-bold text-gray-900 mb-4">Path Not Found</h1>
          <Link 
            href="/" 
            className="text-[#cc9543] hover:underline inline-flex items-center"
          >
            <ChevronLeft className="h-4 w-4 mr-1" />
            Back to Paths
          </Link>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header Section */}
      <div className="bg-white border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          <Link 
            href="/" 
            className="text-gray-500 hover:text-gray-900 inline-flex items-center mb-4"
          >
            <ChevronLeft className="h-4 w-4 mr-1" />
            Back to Paths
          </Link>

          <div className="flex flex-col md:flex-row md:items-start md:justify-between gap-6">
            <div className="flex-1">
              <div className="flex items-center gap-2 mb-2">
                <span className="px-3 py-1 text-sm font-medium text-[#cc9543] bg-orange-50 rounded-full">
                  {path.language} {path.version}
                </span>
                <span className="px-3 py-1 text-sm font-medium text-gray-600 bg-gray-100 rounded-full">
                  {path.area}
                </span>
              </div>
              <h1 className="text-4xl font-bold text-gray-900 mb-4">{path.title}</h1>
              <p className="text-lg text-gray-600 max-w-3xl">{path.description}</p>
            </div>

            <div className="bg-gray-50 rounded-lg p-6 min-w-[280px]">
              <div className="mb-4">
                <div className="flex items-center justify-between mb-2">
                  <span className="text-gray-600">Progress</span>
                  <span className="text-2xl font-bold text-[#cc9543]">{completionPercentage}%</span>
                </div>
                <div className="w-full bg-gray-200 rounded-full h-3">
                  <div 
                    className="bg-[#cc9543] h-3 rounded-full transition-all duration-500"
                    style={{ width: `${completionPercentage}%` }}
                  />
                </div>
              </div>
              <div className="space-y-2 text-sm text-gray-600">
                <div className="flex items-center justify-between">
                  <span>Tasks Completed</span>
                  <span className="font-medium">
                    {progress.completedTasks.length} / {path.totalTasks}
                  </span>
                </div>
                <div className="flex items-center justify-between">
                  <span>Estimated Time</span>
                  <span className="font-medium">{path.estimatedHours} hours</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Phases and Tasks */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        <div className="space-y-12">
          {path.phases.map((phase, phaseIndex) => (
            <div key={phase.id} className="bg-white rounded-lg border border-gray-200 overflow-hidden">
              <div className="bg-gray-50 px-6 py-4 border-b border-gray-200">
                <div className="flex items-center gap-3">
                  <div className="w-10 h-10 bg-[#cc9543] text-white rounded-full flex items-center justify-center font-bold">
                    {phaseIndex + 1}
                  </div>
                  <div>
                    <h2 className="text-xl font-bold text-gray-900">{phase.title}</h2>
                    <p className="text-gray-600 text-sm">{phase.description}</p>
                  </div>
                </div>
              </div>

              <div className="divide-y divide-gray-100">
                {phase.tasks.map((task, taskIndex) => {
                  const isCompleted = progress.completedTasks.includes(task.id);
                  const TaskIcon = isCompleted ? CheckCircle2 : Circle;
                  
                  return (
                    <Link
                      key={task.id}
                      href={`/tasks/${pathId}/${task.id}`}
                      className="flex items-center gap-4 p-6 hover:bg-gray-50 transition-colors group"
                    >
                      <div className="flex-shrink-0">
                        <TaskIcon 
                          className={`h-6 w-6 ${isCompleted ? 'text-green-500' : 'text-gray-300 group-hover:text-gray-400'}`} 
                        />
                      </div>

                      <div className="flex-1 min-w-0">
                        <div className="flex items-center gap-3 mb-1">
                          <span className="text-sm text-gray-400">
                            {phaseIndex + 1}.{taskIndex + 1}
                          </span>
                          <h3 className={`font-semibold ${isCompleted ? 'text-gray-700' : 'text-gray-900'}`}>
                            {task.title}
                          </h3>
                        </div>
                        <p className="text-sm text-gray-600 line-clamp-1">
                          {task.description}
                        </p>
                      </div>

                      <div className="flex items-center gap-4 text-sm text-gray-500">
                        <div className="flex items-center gap-1">
                          <Clock className="h-4 w-4" />
                          <span>{task.estimatedHours}h</span>
                        </div>
                        <div className="flex items-center gap-1">
                          <span className="font-medium">Difficulty:</span>
                          <span className="inline-flex">
                            {Array.from({ length: 5 }).map((_, i) => (
                              <span
                                key={i}
                                className={`w-2 h-2 rounded-full mx-0.5 ${
                                  i < task.difficulty ? 'bg-[#cc9543]' : 'bg-gray-200'
                                }`}
                              />
                            ))}
                          </span>
                        </div>
                        <ArrowRight className="h-5 w-5 text-gray-300 group-hover:text-[#cc9543] transition-colors" />
                      </div>
                    </Link>
                  );
                })}
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
