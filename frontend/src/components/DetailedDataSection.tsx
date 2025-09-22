import React, { useState } from 'react';
import { ResponseAnalyzer } from '../utils/responseAnalyzer';

interface DetailedDataSectionProps {
  content: string;
  isExpanded?: boolean;
}

export const DetailedDataSection: React.FC<DetailedDataSectionProps> = ({
  content,
  isExpanded = false
}) => {
  const [expanded, setExpanded] = useState(isExpanded);
  const [activeTab, setActiveTab] = useState<'insights' | 'comparisons' | 'statistics' | 'quality'>('insights');

  // Analyze the content
  const insights = ResponseAnalyzer.extractInsights(content);
  const comparisons = ResponseAnalyzer.detectComparisons(content);
  const statistics = ResponseAnalyzer.extractStatisticsWithContext(content);
  const quality = ResponseAnalyzer.assessDataQuality(content);

  const tabs = [
    { id: 'insights', label: 'Insights', count: insights.length },
    { id: 'comparisons', label: 'Comparisons', count: comparisons.length },
    { id: 'statistics', label: 'Statistics', count: statistics.length },
    { id: 'quality', label: 'Quality', count: quality.score }
  ] as const;

  const getQualityColor = (score: number) => {
    if (score >= 6) return 'text-green-600 bg-green-50 border-green-200';
    if (score >= 4) return 'text-yellow-600 bg-yellow-50 border-yellow-200';
    return 'text-red-600 bg-red-50 border-red-200';
  };

  const getQualityText = (score: number) => {
    if (score >= 6) return 'High Quality';
    if (score >= 4) return 'Medium Quality';
    return 'Low Quality';
  };

  return (
    <div className="detailed-data-section bg-white rounded-lg shadow-sm border border-gray-200 overflow-hidden">
      <button
        onClick={() => setExpanded(!expanded)}
        className="w-full px-4 py-3 flex items-center justify-between hover:bg-gray-50 transition-colors"
        aria-expanded={expanded}
      >
        <div className="flex items-center gap-2">
          <span className="text-lg">🔍</span>
          <h3 className="text-lg font-semibold text-gray-900">Detailed Analysis</h3>
          <span className="text-sm text-gray-500">
            ({insights.length + comparisons.length + statistics.length} items)
          </span>
        </div>
        <svg
          className={`w-5 h-5 text-gray-500 transition-transform ${expanded ? 'rotate-180' : ''}`}
          fill="none"
          stroke="currentColor"
          viewBox="0 0 24 24"
        >
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
        </svg>
      </button>

      {expanded && (
        <div className="border-t border-gray-200">
          {/* Tabs */}
          <div className="flex border-b border-gray-200">
            {tabs.map((tab) => (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`px-4 py-2 text-sm font-medium transition-colors ${
                  activeTab === tab.id
                    ? 'text-blue-600 border-b-2 border-blue-600 bg-blue-50'
                    : 'text-gray-500 hover:text-gray-700 hover:bg-gray-50'
                }`}
              >
                {tab.label}
                {tab.count > 0 && (
                  <span className="ml-2 px-2 py-0.5 text-xs rounded-full bg-gray-200 text-gray-700">
                    {tab.count}
                  </span>
                )}
              </button>
            ))}
          </div>

          {/* Tab Content */}
          <div className="p-4">
            {activeTab === 'insights' && (
              <div className="space-y-3">
                {insights.length > 0 ? (
                  insights.map((insight, index) => (
                    <div key={index} className="p-3 bg-blue-50 rounded-lg border border-blue-200">
                      <div className="flex items-start gap-2">
                        <span className="text-blue-500 mt-1">💡</span>
                        <p className="text-sm text-blue-900">{insight}</p>
                      </div>
                    </div>
                  ))
                ) : (
                  <p className="text-gray-500 text-center py-4">No insights detected in this content.</p>
                )}
              </div>
            )}

            {activeTab === 'comparisons' && (
              <div className="space-y-3">
                {comparisons.length > 0 ? (
                  comparisons.map((comparison, index) => (
                    <div key={index} className="p-3 bg-purple-50 rounded-lg border border-purple-200">
                      <div className="flex items-center justify-between mb-2">
                        <span className="text-xs font-medium text-purple-600 uppercase">
                          {comparison.type}
                        </span>
                      </div>
                      <div className="text-sm text-purple-900 font-medium">
                        {comparison.item1} vs {comparison.item2}
                      </div>
                      {comparison.value1 && comparison.value2 && (
                        <div className="text-xs text-purple-700 mt-1">
                          {comparison.value1} vs {comparison.value2}
                        </div>
                      )}
                      <div className="text-xs text-purple-600 mt-2">
                        {comparison.fullText}
                      </div>
                    </div>
                  ))
                ) : (
                  <p className="text-gray-500 text-center py-4">No comparisons detected in this content.</p>
                )}
              </div>
            )}

            {activeTab === 'statistics' && (
              <div className="space-y-3">
                {statistics.length > 0 ? (
                  statistics.map((stat, index) => (
                    <div key={index} className="p-3 bg-green-50 rounded-lg border border-green-200">
                      <div className="flex items-center justify-between">
                        <div className="stat-value font-bold text-green-900 text-lg">
                          {stat.value}
                          {stat.unit && <span className="text-sm font-normal ml-1">{stat.unit}</span>}
                        </div>
                        <span className="text-xs text-green-600">
                          Line {stat.position.line + 1}
                        </span>
                      </div>
                      <div className="text-xs text-green-700 mt-2">
                        Context: {stat.context}
                      </div>
                    </div>
                  ))
                ) : (
                  <p className="text-gray-500 text-center py-4">No statistics detected in this content.</p>
                )}
              </div>
            )}

            {activeTab === 'quality' && (
              <div className="space-y-4">
                <div className={`p-4 rounded-lg border ${getQualityColor(quality.score)}`}>
                  <div className="flex items-center justify-between mb-3">
                    <span className="font-medium">Overall Quality Score</span>
                    <span className="text-2xl font-bold">{quality.score}/8</span>
                  </div>
                  <span className="text-sm">{getQualityText(quality.score)}</span>
                </div>

                <div className="space-y-2">
                  <div className="flex items-center justify-between p-2 bg-gray-50 rounded">
                    <span className="text-sm text-gray-700">Has Structure</span>
                    <span className={`text-sm font-medium ${quality.hasStructure ? 'text-green-600' : 'text-red-600'}`}>
                      {quality.hasStructure ? '✓' : '✗'}
                    </span>
                  </div>
                  <div className="flex items-center justify-between p-2 bg-gray-50 rounded">
                    <span className="text-sm text-gray-700">Has Comparisons</span>
                    <span className={`text-sm font-medium ${quality.hasComparisons ? 'text-green-600' : 'text-red-600'}`}>
                      {quality.hasComparisons ? '✓' : '✗'}
                    </span>
                  </div>
                  <div className="flex items-center justify-between p-2 bg-gray-50 rounded">
                    <span className="text-sm text-gray-700">Has Statistics</span>
                    <span className={`text-sm font-medium ${quality.hasStatistics ? 'text-green-600' : 'text-red-600'}`}>
                      {quality.hasStatistics ? '✓' : '✗'}
                    </span>
                  </div>
                  <div className="flex items-center justify-between p-2 bg-gray-50 rounded">
                    <span className="text-sm text-gray-700">Has Sources</span>
                    <span className={`text-sm font-medium ${quality.hasSources ? 'text-green-600' : 'text-red-600'}`}>
                      {quality.hasSources ? '✓' : '✗'}
                    </span>
                  </div>
                  <div className="flex items-center justify-between p-2 bg-gray-50 rounded">
                    <span className="text-sm text-gray-700">Has Insights</span>
                    <span className={`text-sm font-medium ${quality.hasInsights ? 'text-green-600' : 'text-red-600'}`}>
                      {quality.hasInsights ? '✓' : '✗'}
                    </span>
                  </div>
                </div>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
};