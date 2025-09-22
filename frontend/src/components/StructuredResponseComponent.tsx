import React, { useState } from 'react';
import { StructuredResponse } from '../types';
import { ResponseSection } from './ResponseSection';
import { HowToSection } from './HowToSection';
import { ReferencesSection } from './ReferencesSection';
import { CustomSection } from './CustomSection';

interface StructuredResponseComponentProps {
  response: StructuredResponse;
}

export const StructuredResponseComponent: React.FC<StructuredResponseComponentProps> = ({
  response
}) => {
  const [expandedSections, setExpandedSections] = useState<Set<string>>(new Set());

  const toggleSection = (sectionTitle: string) => {
    setExpandedSections(prev => {
      const newSet = new Set(prev);
      if (newSet.has(sectionTitle)) {
        newSet.delete(sectionTitle);
      } else {
        newSet.add(sectionTitle);
      }
      return newSet;
    });
  };

  const isExpanded = (sectionTitle: string) => expandedSections.has(sectionTitle);

  return (
    <div className="structured-response space-y-6">

      {/* Key Findings */}
      {response.keyFindings && (
        <ResponseSection
          title={response.keyFindings.title}
          type="key-findings"
          isExpanded={isExpanded('key-findings')}
          onToggle={() => toggleSection('key-findings')}
        >
          <div className="space-y-3">
            {response.keyFindings.findings.map((finding, index) => (
              <div key={index} className="finding-item flex items-start gap-3 p-3 bg-gray-50 rounded-lg">
                {finding.icon && <span className="text-lg">{finding.icon}</span>}
                <div className="flex-1">
                  <div className="font-medium text-gray-900">{finding.content}</div>
                  {finding.title && (
                    <div className="text-sm text-gray-600 mt-1">{finding.title}</div>
                  )}
                </div>
              </div>
            ))}
          </div>
        </ResponseSection>
      )}

      {/* How to Use */}
      {response.howToUse && (
        <HowToSection 
          section={response.howToUse}
          isExpanded={isExpanded('how-to')}
          onToggle={() => toggleSection('how-to')}
        />
      )}

      {/* Coverage */}
      {response.coverage && (
        <ResponseSection
          title={response.coverage.title}
          type="coverage"
          isExpanded={isExpanded('coverage')}
          onToggle={() => toggleSection('coverage')}
        >
          <div className="space-y-3">
            <div className="coverage-list">
              <h4 className="font-medium text-gray-700 mb-2">Coverage Areas:</h4>
              <ul className="space-y-1">
                {response.coverage.coverage.map((item, index) => (
                  <li key={index} className="flex items-center gap-2">
                    <span className="w-2 h-2 bg-green-500 rounded-full"></span>
                    <span className="text-gray-600">{item}</span>
                  </li>
                ))}
              </ul>
            </div>
            
            {response.coverage.applicability && (
              <div className="applicability-list">
                <h4 className="font-medium text-gray-700 mb-2">Applicability:</h4>
                <ul className="space-y-1">
                  {response.coverage.applicability.map((item, index) => (
                    <li key={index} className="flex items-center gap-2">
                      <span className="w-2 h-2 bg-blue-500 rounded-full"></span>
                      <span className="text-gray-600">{item}</span>
                    </li>
                  ))}
                </ul>
              </div>
            )}
          </div>
        </ResponseSection>
      )}

      {/* Limitations */}
      {response.limitations && (
        <ResponseSection
          title={response.limitations.title}
          type="limitations"
          isExpanded={isExpanded('limitations')}
          onToggle={() => toggleSection('limitations')}
        >
          <div className="space-y-2">
            {response.limitations.limitations.map((limitation, index) => (
              <div key={index} className="flex items-start gap-2">
                <span className="text-red-500 mt-1">⚠️</span>
                <span className="text-gray-600">{limitation}</span>
              </div>
            ))}
          </div>
        </ResponseSection>
      )}

      {/* Dataset Info */}
      {response.datasetInfo && (
        <ResponseSection
          title={response.datasetInfo.title}
          type="dataset-info"
          isExpanded={isExpanded('dataset-info')}
          onToggle={() => toggleSection('dataset-info')}
        >
          <div className="space-y-3">
            {response.datasetInfo.info.map((info, index) => (
              <div key={index} className="info-item flex justify-between items-center py-2 border-b border-gray-100">
                <span className="font-medium text-gray-700">{info.label}:</span>
                <span className={`text-gray-600 ${info.type === 'number' ? 'font-mono' : ''}`}>
                  {info.value}
                </span>
              </div>
            ))}
          </div>
        </ResponseSection>
      )}

      {/* References */}
      {response.references && (
        <ReferencesSection 
          references={response.references}
          isExpanded={isExpanded('references')}
          onToggle={() => toggleSection('references')}
        />
      )}

      {/* Custom Sections */}
      {response.customSections && response.customSections.map((section, index) => (
        <CustomSection
          key={index}
          section={section}
          isExpanded={isExpanded(`custom-${index}`)}
          onToggle={() => toggleSection(`custom-${index}`)}
        />
      ))}
    </div>
  );
};