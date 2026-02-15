'use client';

import Link from 'next/link';
import { Code2, Menu, X } from 'lucide-react';
import { useState } from 'react';

export function Header() {
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);

  return (
    <header className="bg-white border-b border-gray-200 sticky top-0 z-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between items-center h-16">
          <Link href="/" className="flex items-center space-x-2">
            <Code2 className="h-8 w-8 text-[#cc9543]" />
            <span className="text-xl font-bold text-gray-900">LearnByDoing</span>
          </Link>

          <nav className="hidden md:flex space-x-8">
            <Link 
              href="/" 
              className="text-gray-600 hover:text-gray-900 font-medium transition-colors"
            >
              Paths
            </Link>
            <Link 
              href="/about" 
              className="text-gray-600 hover:text-gray-900 font-medium transition-colors"
            >
              About
            </Link>
          </nav>

          <button
            className="md:hidden p-2 text-gray-600 hover:text-gray-900"
            onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
          >
            {mobileMenuOpen ? <X className="h-6 w-6" /> : <Menu className="h-6 w-6" />}
          </button>
        </div>

        {mobileMenuOpen && (
          <div className="md:hidden py-4 border-t border-gray-200">
            <nav className="flex flex-col space-y-4">
              <Link 
                href="/" 
                className="text-gray-600 hover:text-gray-900 font-medium"
                onClick={() => setMobileMenuOpen(false)}
              >
                Paths
              </Link>
              <Link 
                href="/about" 
                className="text-gray-600 hover:text-gray-900 font-medium"
                onClick={() => setMobileMenuOpen(false)}
              >
                About
              </Link>
            </nav>
          </div>
        )}
      </div>
    </header>
  );
}
