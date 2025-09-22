import React from 'react';
import { OverviewSection } from '../types';

interface OverviewCardProps {
  overview: OverviewSection;
  isExpanded: boolean;
  onToggle: () => void;
}

export const OverviewCard: React.FC<OverviewCardProps> = ({
  overview,
  isExpanded,
  onToggle
}) => {
  return (
    <div className="overview-card bg-white rounded-lg shadow-sm border border-gray-200 overflow-hidden">
      <button
        onClick={onToggle}
        className="w-full px-4 py-3 flex items-center justify-between hover:bg-gray-50 transition-colors"
        aria-expanded={isExpanded}
      >
        <h3 className="text-lg font-semibold text-gray-900">{overview.title}</h3>
        <svg
          className={`w-5 h-5 text-gray-500 transition-transform ${isExpanded ? 'rotate-180' : ''}`}
          fill="none"
          stroke="currentColor"
          viewBox="0 0 24 24"
        >
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
        </svg>
      </button>

      {isExpanded && (
        <div className="px-4 pb-4">
          {/* Content */}
          <div className="text-gray-700 leading-relaxed mb-4">
            {overview.content}
          </div>

          {/* Key Stats */}
          {overview.keyStats && overview.keyStats.length > 0 && (
            <div className="key-stats">
              <h4 className="font-medium text-gray-700 mb-3">Key Statistics:</h4>
              <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3">
                {overview.keyStats.map((stat, index) => (
                  <div 
                    key={index}
                    className={`stat-item p-3 rounded-lg border ${
                      stat.highlighted 
                        ? 'border-blue-200 bg-blue-50' 
                        : 'border-gray-200 bg-gray-50'
                    }`}
                  >
                    <div className="flex items-baseline justify-between">
                      <div className="stat-value font-bold text-xl text-gray-900">
                        {stat.value}
                      </div>
                      {stat.unit && (
                        <div className="stat-unit text-sm text-gray-500 ml-1">
                          {stat.unit}
                        </div>
                      )}
                    </div>
                    <div className="stat-label text-sm text-gray-600 mt-1">
                      {stat.label}
                    </div>
                    {stat.comparison && (
                      <div className="stat-comparison text-xs text-gray-500 mt-1">
                        {stat.comparison}
                      </div>
                    )}
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
};