import React from 'react';

interface ResponseSectionProps {
  title: string;
  type: string;
  isExpanded: boolean;
  onToggle: () => void;
  children: React.ReactNode;
}

export const ResponseSection: React.FC<ResponseSectionProps> = ({
  title,
  type,
  isExpanded,
  onToggle,
  children
}) => {
  const getSectionIcon = (sectionType: string) => {
    const iconMap: Record<string, string> = {
      'key-findings': '🎯',
      'coverage': '📊',
      'limitations': '⚠️',
      'dataset-info': '📁',
      'references': '📚',
      'how-to': '📝',
      'comparison': '🔍'
    };
    return iconMap[sectionType] || '📋';
  };

  const getSectionColor = (sectionType: string) => {
    const colorMap: Record<string, string> = {
      'key-findings': 'bg-blue-50 border-blue-200',
      'coverage': 'bg-green-50 border-green-200',
      'limitations': 'bg-red-50 border-red-200',
      'dataset-info': 'bg-purple-50 border-purple-200',
      'references': 'bg-gray-50 border-gray-200',
      'how-to': 'bg-indigo-50 border-indigo-200',
      'comparison': 'bg-yellow-50 border-yellow-200'
    };
    return colorMap[sectionType] || 'bg-gray-50 border-gray-200';
  };

  return (
    <div className={`response-section rounded-lg border overflow-hidden ${getSectionColor(type)}`}>
      <button
        onClick={onToggle}
        className="w-full px-4 py-3 flex items-center justify-between hover:bg-opacity-80 transition-colors"
        aria-expanded={isExpanded}
      >
        <div className="flex items-center gap-2">
          <span className="text-lg">{getSectionIcon(type)}</span>
          <h3 className="text-lg font-semibold text-gray-900">{title}</h3>
        </div>
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
          {children}
        </div>
      )}
    </div>
  );
};