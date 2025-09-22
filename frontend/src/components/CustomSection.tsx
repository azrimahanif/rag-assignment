import React from 'react';
import { CustomSection as CustomSectionType } from '../types';

interface CustomSectionProps {
  section: CustomSectionType;
  isExpanded: boolean;
  onToggle: () => void;
}

export const CustomSection: React.FC<CustomSectionProps> = ({
  section,
  isExpanded,
  onToggle
}) => {
  const getSectionIcon = (type: string) => {
    const iconMap: Record<string, string> = {
      'list': '📋',
      'table': '📊',
      'text': '📝',
      'comparison': '🔍'
    };
    return iconMap[type] || '📄';
  };

  const renderContent = () => {
    switch (section.type) {
      case 'list':
        return (
          <div className="space-y-2">
            {(section.items || []).map((item, index) => (
              <div key={index} className="flex items-start gap-2">
                <span className="text-gray-400 mt-1">•</span>
                <span className="text-gray-700">{item}</span>
              </div>
            ))}
          </div>
        );

      case 'table':
        if (section.data && Array.isArray(section.data)) {
          return (
            <div className="overflow-x-auto">
              <table className="w-full border-collapse border border-gray-300">
                <thead>
                  <tr className="bg-gray-100">
                    {Object.keys(section.data[0] || {}).map((key, index) => (
                      <th key={index} className="border border-gray-300 px-3 py-2 text-left font-medium text-gray-700">
                        {key}
                      </th>
                    ))}
                  </tr>
                </thead>
                <tbody>
                  {section.data.map((row, rowIndex) => (
                    <tr key={rowIndex} className={rowIndex % 2 === 0 ? 'bg-white' : 'bg-gray-50'}>
                      {Object.values(row).map((value, colIndex) => (
                        <td key={colIndex} className="border border-gray-300 px-3 py-2 text-gray-700">
                          {String(value)}
                        </td>
                      ))}
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          );
        }
        return <div className="text-gray-500">No table data available</div>;

      case 'comparison':
        return (
          <div className="space-y-3">
            <div className="text-gray-700 leading-relaxed">
              {section.content}
            </div>
            {section.items && section.items.length > 0 && (
              <div className="grid grid-cols-1 md:grid-cols-2 gap-3 mt-4">
                {section.items.map((item, index) => (
                  <div key={index} className="p-3 bg-gray-50 rounded-lg border border-gray-200">
                    <span className="text-gray-700">{item}</span>
                  </div>
                ))}
              </div>
            )}
          </div>
        );

      case 'text':
      default:
        return (
          <div className="text-gray-700 leading-relaxed whitespace-pre-wrap">
            {section.content}
          </div>
        );
    }
  };

  return (
    <div className="custom-section bg-white rounded-lg shadow-sm border border-gray-200 overflow-hidden">
      <button
        onClick={onToggle}
        className="w-full px-4 py-3 flex items-center justify-between hover:bg-gray-50 transition-colors"
        aria-expanded={isExpanded}
      >
        <div className="flex items-center gap-2">
          <span className="text-lg">{getSectionIcon(section.type)}</span>
          <h3 className="text-lg font-semibold text-gray-900">{section.title}</h3>
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
          {renderContent()}
        </div>
      )}
    </div>
  );
};