import React from 'react';
import { ReferencesSection as ReferencesSectionType } from '../types';

interface ReferencesSectionProps {
  references: ReferencesSectionType;
  isExpanded: boolean;
  onToggle: () => void;
}

export const ReferencesSection: React.FC<ReferencesSectionProps> = ({
  references,
  isExpanded,
  onToggle
}) => {
  const getSourceIcon = (type: string) => {
    const iconMap: Record<string, string> = {
      'dataset': '📊',
      'document': '📄',
      'link': '🔗'
    };
    return iconMap[type] || '📚';
  };

  return (
    <div className="references-section bg-white rounded-lg shadow-sm border border-gray-200 overflow-hidden">
      <button
        onClick={onToggle}
        className="w-full px-4 py-3 flex items-center justify-between hover:bg-gray-50 transition-colors"
        aria-expanded={isExpanded}
      >
        <div className="flex items-center gap-2">
          <span className="text-lg">📚</span>
          <h3 className="text-lg font-semibold text-gray-900">{references.title}</h3>
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
        <div className="p-4">
          <div className="space-y-3">
            {references.sources.map((source, index) => (
              <div key={index} className="source-item p-3 bg-gray-50 rounded-lg border border-gray-200">
                <div className="flex items-start gap-3">
                  <span className="text-lg mt-1">{getSourceIcon(source.type)}</span>
                  <div className="flex-1">
                    <div className="source-title font-medium text-gray-900 mb-1">
                      {source.title}
                    </div>
                    {source.url && (
                      <a
                        href={source.url}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="source-url text-sm text-blue-600 hover:text-blue-800 underline"
                      >
                        {source.url}
                      </a>
                    )}
                    {source.description && (
                      <div className="source-description text-sm text-gray-600 mt-2">
                        {source.description}
                      </div>
                    )}
                    <div className="source-type text-xs text-gray-500 mt-2">
                      Type: {source.type}
                    </div>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};