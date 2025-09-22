import React, { useState, useEffect } from 'react';
import { X, Search, FileText, ChevronLeft, ChevronRight } from 'lucide-react';
import { SourceCard } from './SourceCard';
import type { SourceItem } from '../types';

interface SourcePanelProps {
  sources: SourceItem[];
  title?: string;
  theme?: 'light' | 'dark' | 'system';
  currentMessageId?: string | null;
  currentMessageIndex?: number;
  totalMessagesWithSources?: number;
  onNavigateMessage?: (direction: 'next' | 'prev') => void;
}

type SortOption = 'relevance' | 'title' | 'date';
type FilterOption = 'all' | 'high-relevance' | 'has-snippet';

export const SourcePanel: React.FC<SourcePanelProps> = ({
  sources,
  title = 'Sources & References',
  theme = 'light',
  currentMessageId,
  currentMessageIndex = 0,
  totalMessagesWithSources = 0,
  onNavigateMessage
}) => {
  const [searchTerm, setSearchTerm] = useState('');
  const [sortBy, setSortBy] = useState<SortOption>('relevance');
  const [filterBy, setFilterBy] = useState<FilterOption>('all');
  const [filteredSources, setFilteredSources] = useState<SourceItem[]>(sources);

  
  // Filter and sort sources
  useEffect(() => {
    let processed = [...sources];

    // Apply search filter
    if (searchTerm) {
      processed = processed.filter(source =>
        source.title.toLowerCase().includes(searchTerm.toLowerCase()) ||
        (source.snippet && source.snippet.toLowerCase().includes(searchTerm.toLowerCase()))
      );
    }

    // Apply relevance filter
    if (filterBy === 'high-relevance') {
      processed = processed.slice(0, Math.ceil(processed.length * 0.7));
    } else if (filterBy === 'has-snippet') {
      processed = processed.filter(source => source.snippet);
    }

    // Apply sorting
    processed.sort((a, b) => {
      switch (sortBy) {
        case 'title':
          return a.title.localeCompare(b.title);
        case 'date':
          return (b.url || '').localeCompare(a.url || '');
        default: // relevance
          return sources.indexOf(a) - sources.indexOf(b);
      }
    });

    setFilteredSources(processed);
  }, [sources, searchTerm, sortBy, filterBy]);

  const handleCopy = (text: string) => {
    // You could add a toast notification here
  };

  if (sources.length === 0) return null;

  return (
    <>
      {/* Source Panel */}
      <div className={`
        hidden xl:flex xl:w-80 xl:h-full xl:border-l xl:flex-col
        ${theme === 'dark' ? 'bg-gray-800 border-gray-700' : 'bg-white border-gray-200'}
      `}>
      {/* Header */}
      <div className={`flex flex-col p-4 border-b ${
        theme === 'dark' ? 'border-gray-700 bg-gray-800' : 'border-gray-200 bg-white'
      }`}>
        {/* Main Header Row */}
        <div className="flex items-center justify-between mb-3">
          <div className="flex items-center gap-3">
            <div className="flex items-center gap-2">
              <FileText className={`w-5 h-5 ${theme === 'dark' ? 'text-blue-400' : 'text-blue-600'}`} />
              <h2 className={`text-lg font-semibold ${theme === 'dark' ? 'text-gray-100' : 'text-gray-900'}`}>
                {title}
              </h2>
            </div>
            <span className={`px-2 py-1 text-xs font-medium rounded-full ${
              theme === 'dark' ? 'bg-blue-900 text-blue-300' : 'bg-blue-100 text-blue-700'
            }`}>
              {filteredSources.length} {filteredSources.length === 1 ? 'Source' : 'Sources'}
            </span>
          </div>
        </div>

          {/* Navigation Controls */}
          {totalMessagesWithSources > 1 && (
            <div className={`flex items-center justify-between px-2 py-2 rounded-lg ${
              theme === 'dark' ? 'bg-gray-700' : 'bg-gray-50'
            }`}>
              <button
                onClick={() => onNavigateMessage?.('prev')}
                disabled={!onNavigateMessage}
                className={`flex items-center gap-2 px-3 py-1 rounded transition-colors ${
                  onNavigateMessage
                    ? theme === 'dark'
                      ? 'text-gray-300 hover:bg-gray-600 hover:text-white'
                      : 'text-gray-600 hover:bg-gray-200 hover:text-gray-900'
                    : 'text-gray-400 cursor-not-allowed'
                }`}
                title="Previous message sources"
              >
                <ChevronLeft className="w-4 h-4" />
                <span className="text-sm">Previous</span>
              </button>

              <div className="flex flex-col items-center">
                <span className={`text-xs ${theme === 'dark' ? 'text-gray-400' : 'text-gray-500'}`}>
                  Message {currentMessageIndex! + 1} of {totalMessagesWithSources}
                </span>
                {currentMessageId && (
                  <span className={`text-xs ${theme === 'dark' ? 'text-gray-500' : 'text-gray-400'}`}>
                    ID: {currentMessageId.slice(-8)}
                  </span>
                )}
              </div>

              <button
                onClick={() => onNavigateMessage?.('next')}
                disabled={!onNavigateMessage}
                className={`flex items-center gap-2 px-3 py-1 rounded transition-colors ${
                  onNavigateMessage
                    ? theme === 'dark'
                      ? 'text-gray-300 hover:bg-gray-600 hover:text-white'
                      : 'text-gray-600 hover:bg-gray-200 hover:text-gray-900'
                    : 'text-gray-400 cursor-not-allowed'
                }`}
                title="Next message sources"
              >
                <span className="text-sm">Next</span>
                <ChevronRight className="w-4 h-4" />
              </button>
            </div>
          )}
        </div>

        {/* Search and Filters */}
        <div className={`p-4 border-b space-y-3 ${
          theme === 'dark' ? 'border-gray-700 bg-gray-800' : 'border-gray-200 bg-white'
        }`}>
          <div className="relative">
            <Search className={`absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 ${
              theme === 'dark' ? 'text-gray-500' : 'text-gray-400'
            }`} />
            <input
              type="text"
              placeholder="Search sources..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className={`w-full pl-10 pr-4 py-2 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent ${
                theme === 'dark'
                  ? 'bg-gray-700 border-gray-600 text-gray-100 placeholder-gray-400'
                  : 'bg-white border border-gray-300 text-gray-900 placeholder-gray-500'
              }`}
            />
          </div>

          <div className="flex gap-2">
            <select
              value={sortBy}
              onChange={(e) => setSortBy(e.target.value as SortOption)}
              className={`flex-1 px-3 py-2 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent text-sm ${
                theme === 'dark'
                  ? 'bg-gray-700 border-gray-600 text-gray-100'
                  : 'bg-white border border-gray-300 text-gray-900'
              }`}
            >
              <option value="relevance">Sort by Relevance</option>
              <option value="title">Sort by Title</option>
              <option value="date">Sort by Date</option>
            </select>

            <select
              value={filterBy}
              onChange={(e) => setFilterBy(e.target.value as FilterOption)}
              className={`flex-1 px-3 py-2 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent text-sm ${
                theme === 'dark'
                  ? 'bg-gray-700 border-gray-600 text-gray-100'
                  : 'bg-white border border-gray-300 text-gray-900'
              }`}
            >
              <option value="all">All Sources</option>
              <option value="high-relevance">High Relevance</option>
              <option value="has-snippet">Has Snippet</option>
            </select>
          </div>
        </div>

        {/* Sources List - Scrollable */}
        <div className="flex-1 overflow-y-auto p-4 space-y-3">
          {filteredSources.length === 0 ? (
            <div className="text-center py-8">
              <FileText className={`w-12 h-12 mx-auto mb-4 ${
                theme === 'dark' ? 'text-gray-600' : 'text-gray-300'
              }`} />
              <p className={`text-sm ${
                theme === 'dark' ? 'text-gray-500' : 'text-gray-500'
              }`}>
                {searchTerm ? 'No sources match your search.' : 'No sources available.'}
              </p>
            </div>
          ) : (
            filteredSources.map((source, index) => (
              <SourceCard
                key={`${source.url}-${index}`}
                source={source}
                index={sources.indexOf(source)}
                onCopy={handleCopy}
              />
            ))
          )}
        </div>
      </div>
    </>
  );
};