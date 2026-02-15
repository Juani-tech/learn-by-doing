'use client';

import Link from 'next/link';
import { LearningPath } from '@/types';
import { Clock, Layers, ChevronRight } from 'lucide-react';

interface PathCardProps {
  path: LearningPath;
  completedCount: number;
}

export function PathCard({ path, completedCount }: PathCardProps) {
  const progress = Math.round((completedCount / path.totalTasks) * 100);

  return (
    <Link 
      href={`/paths/${path.id}`}
      className="block bg-white rounded-lg border border-gray-200 hover:border-[#cc9543] hover:shadow-lg transition-all duration-200 overflow-hidden group"
    >
      <div className="p-6">
        <div className="flex items-start justify-between mb-4">
          <div>
            <span className="inline-block px-3 py-1 text-xs font-semibold text-[#cc9543] bg-orange-50 rounded-full mb-2">
              {path.language} {path.version}
            </span>
            <h3 className="text-xl font-bold text-gray-900 group-hover:text-[#cc9543] transition-colors">
              {path.title}
            </h3>
          </div>
          <ChevronRight className="h-5 w-5 text-gray-400 group-hover:text-[#cc9543] transition-colors" />
        </div>

        <p className="text-gray-600 mb-4 line-clamp-2">
          {path.description}
        </p>

        <div className="flex items-center space-x-6 text-sm text-gray-500">
          <div className="flex items-center space-x-1">
            <Layers className="h-4 w-4" />
            <span>{path.totalTasks} tasks</span>
          </div>
          <div className="flex items-center space-x-1">
            <Clock className="h-4 w-4" />
            <span>{path.estimatedHours} hours</span>
          </div>
        </div>

        {completedCount > 0 && (
          <div className="mt-4">
            <div className="flex items-center justify-between text-sm mb-1">
              <span className="text-gray-600">Progress</span>
              <span className="font-semibold text-[#cc9543]">{progress}%</span>
            </div>
            <div className="w-full bg-gray-200 rounded-full h-2">
              <div 
                className="bg-[#cc9543] h-2 rounded-full transition-all duration-300"
                style={{ width: `${progress}%` }}
              />
            </div>
          </div>
        )}
      </div>
    </Link>
  );
}
