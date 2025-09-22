import React from 'react';
import { Statistic } from '../types';

interface StatComparisonProps {
  stats: Statistic[];
  isExpanded: boolean;
  onToggle: () => void;
}

export const StatComparison: React.FC<StatComparisonProps> = ({
  stats,
  isExpanded,
  onToggle
}) => {
  const getComparisonIcon = (stat1: Statistic, stat2: Statistic) => {
    if (!stat1.value || !stat2.value) return '❓';
    
    const val1 = typeof stat1.value === 'number' ? stat1.value : parseFloat(stat1.value);
    const val2 = typeof stat2.value === 'number' ? stat2.value : parseFloat(stat2.value);
    
    if (val1 > val2) return '📈';
    if (val1 < val2) return '📉';
    return '➡️';
  };

  const getComparisonText = (stat1: Statistic, stat2: Statistic) => {
    if (!stat1.value || !stat2.value) return '';
    
    const val1 = typeof stat1.value === 'number' ? stat1.value : parseFloat(stat1.value);
    const val2 = typeof stat2.value === 'number' ? stat2.value : parseFloat(stat2.value);
    
    if (val1 > val2) return `${stat1.label} is higher than ${stat2.label}`;
    if (val1 < val2) return `${stat1.label} is lower than ${stat2.label}`;
    return `${stat1.label} and ${stat2.label} are equal`;
  };

  const formatValue = (value: string | number, unit?: string) => {
    if (typeof value === 'number') {
      return unit ? `${value.toLocaleString()} ${unit}` : value.toLocaleString();
    }
    return unit ? `${value} ${unit}` : value;
  };

  return (
    <div className="stat-comparison bg-white rounded-lg shadow-sm border border-gray-200 overflow-hidden">
      <button
        onClick={onToggle}
        className="w-full px-4 py-3 flex items-center justify-between hover:bg-gray-50 transition-colors"
        aria-expanded={isExpanded}
      >
        <h3 className="text-lg font-semibold text-gray-900">Statistics Comparison</h3>
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
            {/* Comparison Cards */}
            <div className="comparison-cards grid grid-cols-1 md:grid-cols-2 gap-4">
              {stats.slice(0, 2).map((stat, index) => (
                <div 
                  key={index}
                  className={`comparison-card p-4 rounded-lg border-2 ${
                    stat.highlighted 
                      ? 'border-blue-300 bg-blue-50' 
                      : 'border-gray-200 bg-gray-50'
                  }`}
                >
                  <div className="text-center">
                    <div className="text-2xl font-bold text-gray-900 mb-1">
                      {formatValue(stat.value, stat.unit)}
                    </div>
                    <div className="text-sm text-gray-600">{stat.label}</div>
                    {stat.comparison && (
                      <div className="text-xs text-gray-500 mt-2">{stat.comparison}</div>
                    )}
                  </div>
                </div>
              ))}
            </div>

            {/* Comparison Summary */}
            {stats.length >= 2 && (
              <div className="comparison-summary flex items-center justify-center gap-3 py-3">
                <span className="text-2xl">{getComparisonIcon(stats[0], stats[1])}</span>
                <span className="text-sm text-gray-600 text-center">
                  {getComparisonText(stats[0], stats[1])}
                </span>
              </div>
            )}

            {/* Additional Stats */}
            {stats.length > 2 && (
              <div className="additional-stats grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3">
                {stats.slice(2).map((stat, index) => (
                  <div 
                    key={index}
                    className={`stat-item p-3 rounded-lg border ${
                      stat.highlighted 
                        ? 'border-yellow-200 bg-yellow-50' 
                        : 'border-gray-200 bg-gray-50'
                    }`}
                  >
                    <div className="text-center">
                      <div className="text-lg font-semibold text-gray-900">
                        {formatValue(stat.value, stat.unit)}
                      </div>
                      <div className="text-xs text-gray-600 mt-1">{stat.label}</div>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
};