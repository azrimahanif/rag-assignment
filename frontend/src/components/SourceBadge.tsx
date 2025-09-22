import React from 'react';
import { FileText, ChevronRight } from 'lucide-react';

interface SourceBadgeProps {
  sourceCount: number;
  isActive?: boolean;
  onClick?: () => void;
  onViewSources?: () => void;
  className?: string;
}

export const SourceBadge: React.FC<SourceBadgeProps> = ({
  sourceCount,
  isActive = false,
  onClick,
  onViewSources,
  className = ''
}) => {
  if (sourceCount === 0) return null;

  const handleClick = () => {
    if (onClick) {
      onClick();
    } else if (onViewSources) {
      onViewSources();
    }
  };

  return (
    <button
      onClick={handleClick}
      className={`
        inline-flex items-center gap-2 px-3 py-2 rounded-lg
        transition-all duration-200 ease-in-out
        text-sm font-medium
        hover:shadow-sm active:scale-[0.98]
        focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2
        ${
          isActive
            ? 'bg-blue-100 text-blue-800 border-blue-300'
            : 'bg-blue-50 hover:bg-blue-100 text-blue-700 border-blue-200 hover:border-blue-300'
        }
        ${className}
      `}
      aria-label={`View ${sourceCount} source${sourceCount !== 1 ? 's' : ''}`}
    >
      <FileText className="w-4 h-4" />
      <span>
        {sourceCount} {sourceCount === 1 ? 'Source' : 'Sources'}
      </span>
      <ChevronRight className="w-4 h-4 transition-transform duration-200 group-hover:translate-x-0.5" />
    </button>
  );
};