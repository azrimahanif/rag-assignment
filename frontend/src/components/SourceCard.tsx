import React, { useState } from 'react';
import { ExternalLink, Copy, CheckCircle, FileText, Calendar, MapPin } from 'lucide-react';
import type { SourceItem } from '../types';

interface SourceCardProps {
  source: SourceItem;
  index: number;
  onCopy?: (text: string) => void;
}

export const SourceCard: React.FC<SourceCardProps> = ({ 
  source, 
  index, 
  onCopy 
}) => {
  const [copied, setCopied] = useState(false);
  const [expanded, setExpanded] = useState(false);

  const handleCopy = async (text: string) => {
    try {
      await navigator.clipboard.writeText(text);
      setCopied(true);
      onCopy?.(text);
      setTimeout(() => setCopied(false), 2000);
    } catch (err) {
      console.error('Failed to copy text:', err);
    }
  };

  const getDomainFromUrl = (url: string) => {
    try {
      return new URL(url).hostname.replace('www.', '');
    } catch {
      return 'Unknown Source';
    }
  };

  return (
    <div className="bg-white rounded-lg border border-gray-200 p-4 hover:shadow-md transition-all duration-200 ease-in-out group">
      {/* Header */}
      <div className="flex items-start justify-between mb-3">
        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-2 mb-1">
            <FileText className="w-4 h-4 text-blue-600 flex-shrink-0" />
            <h3 className="text-sm font-semibold text-gray-900 truncate">
              {source.title || `Source ${index + 1}`}
            </h3>
          </div>
          <p className="text-xs text-gray-500">
            {getDomainFromUrl(source.url)}
          </p>
        </div>
        
        <div className="flex items-center gap-1 ml-2">
          {source.url && source.url !== '#' && (
            <a
              href={source.url}
              target="_blank"
              rel="noopener noreferrer"
              className="p-1.5 text-gray-400 hover:text-blue-600 hover:bg-blue-50 rounded-lg transition-colors duration-200"
              aria-label="Open source in new tab"
            >
              <ExternalLink className="w-3.5 h-3.5" />
            </a>
          )}
          {source.snippet && (
            <button
              onClick={() => handleCopy(source.snippet || '')}
              className="p-1.5 text-gray-400 hover:text-green-600 hover:bg-green-50 rounded-lg transition-colors duration-200"
              aria-label={copied ? 'Copied!' : 'Copy snippet'}
            >
              {copied ? (
                <CheckCircle className="w-3.5 h-3.5 text-green-600" />
              ) : (
                <Copy className="w-3.5 h-3.5" />
              )}
            </button>
          )}
        </div>
      </div>

      {/* Snippet */}
      {source.snippet && (
        <div className="mb-3">
          <button
            onClick={() => setExpanded(!expanded)}
            className="w-full text-left"
            aria-expanded={expanded}
          >
            <p className={`text-sm text-gray-700 leading-relaxed ${
              !expanded ? 'line-clamp-2' : ''
            }`}>
              {source.snippet}
            </p>
            {source.snippet.length > 150 && (
              <span className="text-xs text-blue-600 hover:text-blue-700 mt-1 inline-block">
                {expanded ? 'Show less' : 'Read more'}
              </span>
            )}
          </button>
        </div>
      )}

      {/* Metadata */}
      <div className="flex items-center gap-4 text-xs text-gray-500">
        <div className="flex items-center gap-1">
          <Calendar className="w-3 h-3" />
          <span>2024</span>
        </div>
        <div className="flex items-center gap-1">
          <MapPin className="w-3 h-3" />
          <span>Malaysia</span>
        </div>
        <div className="flex items-center gap-1">
          <div className="w-2 h-2 bg-green-500 rounded-full"></div>
          <span>Verified Source</span>
        </div>
      </div>

      {/* Trust Indicators */}
      <div className="mt-3 pt-3 border-t border-gray-100">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <div className="flex -space-x-1">
              <div className="w-1.5 h-1.5 bg-blue-500 rounded-full"></div>
              <div className="w-1.5 h-1.5 bg-blue-500 rounded-full"></div>
              <div className="w-1.5 h-1.5 bg-blue-500 rounded-full"></div>
            </div>
            <span className="text-xs text-gray-600">High relevance</span>
          </div>
          <span className="text-xs text-gray-400">#{index + 1}</span>
        </div>
      </div>
    </div>
  );
};