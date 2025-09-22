import React from 'react';
import { HowToSection as HowToSectionType } from '../types';

interface HowToSectionProps {
  section: HowToSectionType;
  isExpanded: boolean;
  onToggle: () => void;
}

export const HowToSection: React.FC<HowToSectionProps> = ({
  section,
  isExpanded,
  onToggle
}) => {
  return (
    <div className="how-to-section bg-white rounded-lg shadow-sm border border-indigo-200 overflow-hidden">
      <button
        onClick={onToggle}
        className="w-full px-4 py-3 flex items-center justify-between hover:bg-indigo-50 transition-colors"
        aria-expanded={isExpanded}
      >
        <div className="flex items-center gap-2">
          <span className="text-lg">📝</span>
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
        <div className="p-4">
          <div className="space-y-4">
            {section.steps.map((step, index) => (
              <div key={index} className="step-item flex gap-4 p-4 bg-gray-50 rounded-lg">
                <div className="step-number flex-shrink-0 w-8 h-8 bg-indigo-500 text-white rounded-full flex items-center justify-center font-semibold text-sm">
                  {step.step}
                </div>
                <div className="step-content flex-1">
                  <div className="step-title font-medium text-gray-900 mb-1">
                    {step.title}
                  </div>
                  <div className="step-description text-gray-600 text-sm">
                    {step.description}
                  </div>
                  {step.action && (
                    <div className="step-action mt-2">
                      <code className="bg-gray-100 px-2 py-1 rounded text-xs text-gray-700">
                        {step.action}
                      </code>
                    </div>
                  )}
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};