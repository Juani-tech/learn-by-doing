'use client';

import { getAllLearningPaths } from '@/lib/paths';
import { getProgress } from '@/lib/storage';
import { PathCard } from '@/components/PathCard';
import { BookOpen, Target, Zap } from 'lucide-react';

export default function Home() {
  const paths = getAllLearningPaths();

  return (
    <div className="min-h-screen">
      {/* Hero Section */}
      <section className="bg-white border-b border-gray-200 py-16 md:py-24">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center max-w-3xl mx-auto">
            <h1 className="text-4xl md:text-6xl font-bold text-gray-900 mb-6">
              Learn by{' '}
              <span className="text-[#cc9543]">Doing</span>
            </h1>
            <p className="text-xl text-gray-600 mb-8">
              No hand-holding. No copy-paste tutorials. Just clear requirements, 
              curated resources, and challenging projects that build real skills.
            </p>
            <div className="flex flex-wrap justify-center gap-4">
              <div className="flex items-center space-x-2 text-gray-600">
                <Target className="h-5 w-5 text-[#cc9543]" />
                <span>Goal-oriented</span>
              </div>
              <div className="flex items-center space-x-2 text-gray-600">
                <BookOpen className="h-5 w-5 text-[#cc9543]" />
                <span>Curated resources</span>
              </div>
              <div className="flex items-center space-x-2 text-gray-600">
                <Zap className="h-5 w-5 text-[#cc9543]" />
                <span>Fast-paced</span>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Learning Paths Section */}
      <section className="py-16">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="mb-12">
            <h2 className="text-3xl font-bold text-gray-900 mb-4">
              Learning Paths
            </h2>
            <p className="text-gray-600 max-w-2xl">
              Choose a path and start building. Each path is designed to take you 
              from fundamentals to production-ready skills through hands-on projects.
            </p>
          </div>

          <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
            {paths.map((path) => {
              const progress = getProgress(path.id);
              return (
                <PathCard 
                  key={path.id} 
                  path={path} 
                  completedCount={progress.completedTasks.length}
                />
              );
            })}
          </div>
        </div>
      </section>

      {/* How It Works Section */}
      <section className="bg-white border-t border-gray-200 py-16">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <h2 className="text-3xl font-bold text-gray-900 mb-12 text-center">
            How It Works
          </h2>
          <div className="grid md:grid-cols-3 gap-8">
            <div className="text-center">
              <div className="w-16 h-16 bg-orange-100 rounded-full flex items-center justify-center mx-auto mb-4">
                <span className="text-2xl font-bold text-[#cc9543]">1</span>
              </div>
              <h3 className="text-xl font-semibold mb-2">Read Requirements</h3>
              <p className="text-gray-600">
                Each task gives you clear requirements and acceptance criteria. 
                No hints, no solutions - just what you need to build.
              </p>
            </div>
            <div className="text-center">
              <div className="w-16 h-16 bg-orange-100 rounded-full flex items-center justify-center mx-auto mb-4">
                <span className="text-2xl font-bold text-[#cc9543]">2</span>
              </div>
              <h3 className="text-xl font-semibold mb-2">Study Resources</h3>
              <p className="text-gray-600">
                Use curated documentation and references. We filter out tutorials 
                and solutions - you learn by figuring it out yourself.
              </p>
            </div>
            <div className="text-center">
              <div className="w-16 h-16 bg-orange-100 rounded-full flex items-center justify-center mx-auto mb-4">
                <span className="text-2xl font-bold text-[#cc9543]">3</span>
              </div>
              <h3 className="text-xl font-semibold mb-2">Build & Iterate</h3>
              <p className="text-gray-600">
                Write code, test against acceptance criteria, and move on. 
                Fast-paced learning with immediate application.
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* Philosophy Section */}
      <section className="py-16 bg-gray-900 text-white">
        <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
          <h2 className="text-3xl font-bold mb-6">Our Philosophy</h2>
          <blockquote className="text-2xl md:text-3xl font-light italic mb-8">
            &ldquo;The best way to learn programming is by programming.&rdquo;
          </blockquote>
          <p className="text-gray-300 text-lg">
            We believe in bottom-up learning: core concepts first, then build 
            complexity. No repetition unless it serves a purpose. No hand-holding. 
            Just you, the documentation, and a challenge to overcome.
          </p>
        </div>
      </section>
    </div>
  );
}
